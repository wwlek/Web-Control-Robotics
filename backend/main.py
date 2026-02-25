from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from enum import Enum
import httpx
from contextlib import asynccontextmanager
import os

TARGET_BASE_URL = os.getenv("TARGET_BASE_URL", "http://10.177.95.105:8000")


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.client = httpx.AsyncClient(
        base_url=TARGET_BASE_URL,
        timeout=httpx.Timeout(5.0)
    ) 
    yield
    await app.state.client.aclose()


app = FastAPI(
    title="Robot Control API",
    lifespan=lifespan
)


class Direction(str, Enum):
    forward = "forward"
    backward = "backward"
    left = "left"
    right = "right"


class MoveRequest(BaseModel):
    direction: Direction


async def forward_post(path: str, payload: dict | None = None):
    try:
        response = await app.state.client.post(path, json=payload)
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
    result = await forward_post("/move", {"direction": request.direction})
    return {"status": "forwarded", "target_response": result}


@app.post("/stop")
async def stop():
    result = await forward_post("/stop")
    return {"status": "forwarded", "target_response": result}


@app.post("/dance")
async def dance():
    result = await forward_post("/dance")
    return {"status": "forwarded", "target_response": result}
