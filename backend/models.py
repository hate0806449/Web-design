"""SQLAlchemy ORM — Video + Snapshot（1:N，CASCADE 刪除）。

舊版是 dataclass，這版正式接 Postgres。
schema 跟 docker-compose 起的 ig_tracker DB 對齊。
"""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship


def _cuid() -> str:
    # 25 字元 short id，比 uuid 漂亮
    return str(uuid4()).replace("-", "")[:25]


class Base(DeclarativeBase):
    pass


class Video(Base):
    __tablename__ = "Video"

    id = Column(String, primary_key=True, default=_cuid)
    platform = Column(String, default="IG")
    shortcode = Column(String, unique=True, nullable=False)
    mediaId = Column("mediaId", String)
    username = Column(String)
    caption = Column(String)
    uploadedAt = Column("uploadedAt", DateTime)
    createdAt = Column(
        "createdAt", DateTime, default=lambda: datetime.now(timezone.utc)
    )

    snapshots = relationship(
        "Snapshot",
        back_populates="video",
        cascade="all, delete-orphan",
        order_by="Snapshot.scrapedAt.desc()",
    )


class Snapshot(Base):
    __tablename__ = "Snapshot"

    id = Column(String, primary_key=True, default=_cuid)
    videoId = Column(
        "videoId",
        String,
        ForeignKey("Video.id", ondelete="CASCADE"),
        nullable=False,
    )
    views = Column(Integer)
    igViews = Column("igViews", Integer)
    fbViews = Column("fbViews", Integer)
    likes = Column(Integer)
    comments = Column(Integer)
    shares = Column(Integer)
    scrapedAt = Column(
        "scrapedAt", DateTime, default=lambda: datetime.now(timezone.utc)
    )

    video = relationship("Video", back_populates="snapshots")

    __table_args__ = (
        Index("Snapshot_videoId_scrapedAt_idx", "videoId", scrapedAt.desc()),
    )


def init_db():
    """第一次跑用，會 create_all。"""
    from database import engine

    Base.metadata.create_all(engine)
