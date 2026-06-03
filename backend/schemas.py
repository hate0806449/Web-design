"""Pydantic response schemas — 對應 ORM model。"""

from pydantic import BaseModel


class SnapshotOut(BaseModel):
    id: str
    videoId: str
    views: int | None = None
    igViews: int | None = None
    fbViews: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None
    scrapedAt: str

    class Config:
        from_attributes = True


class VideoOut(BaseModel):
    id: str
    shortcode: str
    mediaId: str | None = None
    username: str | None = None
    caption: str | None = None
    uploadedAt: str | None = None
    createdAt: str
    latestSnapshot: SnapshotOut | None = None

    class Config:
        from_attributes = True


class VideoWithSnapshots(VideoOut):
    snapshots: list[SnapshotOut] = []

class ReelOut(BaseModel):
    id: str
    shortcode: str
    caption: str
    timestamp: str
    permalink: str
    thumbnailUrl: str | None = None
    plays: int | None = None
    igViews: int | None = None
    fbViews: int | None = None
    likes: int | None = None
    comments: int | None = None
    shares: int | None = None

class IgUser(BaseModel):
    id: str
    username: str
