from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import httpx
from contextlib import asynccontextmanager
import asyncio

CAT_IPS = {
    "1": "http://192.168.1.101",
    "2": "http://192.168.1.102",
    "3": "http://192.168.1.103",
    "4": "http://192.168.1.104",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=httpx.Timeout(5.0))
    app.state.poll_task = asyncio.create_task(update_cat_status())
    yield
    app.state.poll_task.cancel()
    await app.state.client.aclose()

app = FastAPI(title="Robot Control API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Direction(str, Enum):
    forward = "forward"
    backward = "backward"
    left = "left"
    right = "right"

class MoveRequest(BaseModel):
    direction: Direction
    cat: str

class DanceRequest(BaseModel):
    cat: str
    
class WaveRequest(BaseModel):
    cat: str

async def forward_post(cat_ip: str, path: str, payload: dict | None = None):
    try:
        response = await app.state.client.post(f"{cat_ip}{path}", json=payload)
        response.raise_for_status()
        return response.json() if response.content else {}
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)
    except httpx.RequestError:
        raise HTTPException(status_code=502, detail="Could not reach target API")

async def forward_get(cat_ip: str, path: str):
    try:
        response = await app.state.client.get(f"{cat_ip}{path}")
        response.raise_for_status()
        return response.json() if response.content else {}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))
    
@app.post("/move")
async def move(request: MoveRequest):
    cat_ip = CAT_IPS.get(request.cat)
    if not cat_ip:
        raise HTTPException(status_code=404, detail=f"Cat {request.cat} not found")
    result = await forward_post(cat_ip, "/move", {"direction": request.direction})
    return {"status": "forwarded", "target_response": result}

@app.post("/dance")
async def dance(request: DanceRequest):
    targets = CAT_IPS.keys() if request.cat == "all" else [request.cat]

    async def call_cat(cat_id):
        cat_ip = CAT_IPS.get(cat_id)
        if not cat_ip:
            return None
        try:
            res = await forward_post(cat_ip, "/dance")
            return {"cat": cat_id, "response": res}
        except Exception:
            return None

    results = await asyncio.gather(*(call_cat(cat_id) for cat_id in targets))
    results = [r for r in results if r]

    return {
        "status": "forwarded" if results else "no reachable cats",
        "target_responses": results
    }


@app.post("/wave")
async def wave(request: WaveRequest):
    targets = CAT_IPS.keys() if request.cat == "all" else [request.cat]

    async def call_cat(cat_id):
        cat_ip = CAT_IPS.get(cat_id)
        if not cat_ip:
            return None
        try:
            res = await forward_post(cat_ip, "/wave")
            return {"cat": cat_id, "response": res}
        except Exception:
            return None

    results = await asyncio.gather(*(call_cat(cat_id) for cat_id in targets))
    results = [r for r in results if r]

    return {
        "status": "forwarded" if results else "no reachable cats",
        "target_responses": results
    }

MAX_POINTS = 30

cat_status = {
    cat_id: {"voltage": [0] * MAX_POINTS, "battery": 0}
    for cat_id in CAT_IPS
}

async def update_cat_status():
    print("update_cat_status task started")
    while True:
        for cat_id, cat_ip in CAT_IPS.items():
            try:
                print(f"Polling cat {cat_id} at {cat_ip}/status")
                status = await forward_get(cat_ip, "/status")
                v = status.get("voltage", 0)
                cat_status[cat_id]["voltage"] = (
                    cat_status[cat_id]["voltage"] + [v]
                )[-MAX_POINTS:]
                cat_status[cat_id]["battery"] = status.get("battery", 0)
            except Exception:
                pass
        await asyncio.sleep(1)

@app.get("/status")
async def get_status():
    return {
        cat_id: {"voltage": status["voltage"], "battery": status["battery"]}
        for cat_id, status in cat_status.items()
    }