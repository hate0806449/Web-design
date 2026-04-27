"""FastAPI entry — IG Reel Tracker backend (起手式版本)."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import auth, videos

app = FastAPI(title="IG Reel Tracker API")

# dev 階段先全開，上線前要收緊
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(videos.router)


@app.get("/health")
def health():
    return {"status": "ok"}
