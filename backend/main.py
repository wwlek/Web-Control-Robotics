from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from enum import Enum
import httpx
from contextlib import asynccontextmanager
import os

CAT_IPS = {
    "1": "http://10.150.134.220",
    "2": "http://10.150.134.222",
    "3": "http://10.150.134.223",
    "4": "http://10.150.134.224",
}

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(timeout=httpx.Timeout(5.0)) 
    yield
    await app.state.client.aclose()

app = FastAPI(
    title="Robot Control API",
    lifespan=lifespan
)

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

async def forward_post(cat_ip: str, path: str, payload: dict | None = None):
    try:
        response = await app.state.client.post(f"{cat_ip}{path}", json=payload)
        response.raise_for_status()
        return response.json() if response.content else {}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=e.response.text,
        )
    except httpx.RequestError:
        raise HTTPException(
            status_code=502,
            detail="Could not reach target API",
        )

@app.post("/move")
async def move(request: MoveRequest):
    cat_ip = CAT_IPS.get(request.cat)
    
    if not cat_ip:
        raise HTTPException(status_code=404, detail=f"Cat {request.cat} not found")

    result = await forward_post(cat_ip, "/move", {"direction": request.direction})
    return {"status": "forwarded", "target_response": result}

@app.post("/stop")
async def stop(request: MoveRequest):
    if request.cat == "all":
        # Send stop command to all cats
        results = []
        for cat_id, cat_ip in CAT_IPS.items():
            result = await forward_post(cat_ip, "/stop")
            results.append({"cat": cat_id, "response": result})
        return {"status": "forwarded", "target_responses": results}

    cat_ip = CAT_IPS.get(request.cat)
    if not cat_ip:
        raise HTTPException(status_code=404, detail=f"Cat {request.cat} not found")
    
    result = await forward_post(cat_ip, "/stop")
    return {"status": "forwarded", "target_response": result}

@app.post("/dance")
async def dance(request: MoveRequest):
    if request.cat == "all":
        # Send dance command to all cats
        results = []
        for cat_id, cat_ip in CAT_IPS.items():
            result = await forward_post(cat_ip, "/dance")
            results.append({"cat": cat_id, "response": result})
        return {"status": "forwarded", "target_responses": results}

    cat_ip = CAT_IPS.get(request.cat)
    if not cat_ip:
        raise HTTPException(status_code=404, detail=f"Cat {request.cat} not found")
    
    result = await forward_post(cat_ip, "/dance")
    return {"status": "forwarded", "target_response": result}