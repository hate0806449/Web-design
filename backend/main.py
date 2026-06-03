"""FastAPI entry — IG Reel Tracker backend (起手式版本)."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from models import init_db
from routers import auth, videos , reels


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # 啟動時自動 create_all（demo 用，正式環境改用 alembic）
    init_db()
    yield

app = FastAPI(title="IG Reel Tracker API", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(videos.router)
app.include_router(reels.router)


@app.get("/health")
def health():
    return {"status": "ok"}
