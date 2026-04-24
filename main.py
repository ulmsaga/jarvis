"""Jarvis — 팀 자동화 인프라 진입점"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from src.openclaw import memory
from src.slack.app import handler
from src.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await memory.init_db()
    print(f"🤖 Jarvis online — http://{settings.host}:{settings.port}")
    yield


app = FastAPI(title="Jarvis", lifespan=lifespan)


@app.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)


@app.get("/health")
async def health():
    return {"status": "ok", "name": "Jarvis"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=True)
