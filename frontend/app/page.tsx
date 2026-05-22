"use client";

import { useEffect, useState } from "react";
import { AddVideoForm } from "@/components/AddVideoForm";
import { VideoCard } from "@/components/VideoCard";
import { StatsGrid } from "@/components/StatsGrid";
import { VideoWithLatestSnapshot, IgUser } from "@/types";

export default function Home() {
  const [videos, setVideos] = useState<VideoWithLatestSnapshot[]>([]);
  const [user, setUser] = useState<IgUser | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/videos")
      .then((r) => r.json())
      .then((data) => setVideos(data))
      .finally(() => setLoading(false));

    fetch("/api/auth/me")
      .then((r) => r.json())
      .then((data) => setUser(data ?? null));
  }, []);

  function handleAdded(video: VideoWithLatestSnapshot) {
    setVideos((prev) => [video, ...prev]);
  }

  function handleDeleted(id: string) {
    setVideos((prev) => prev.filter((v) => v.id !== id));
  }

  function handleRefreshed(updated: VideoWithLatestSnapshot) {
    setVideos((prev) =>
      prev.map((v) => (v.id === updated.id ? updated : v))
    );
  }

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
  }

  return (
    <div className="min-h-screen bg-zinc-50">
      <div className="max-w-3xl mx-auto px-4 py-8 space-y-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">
              IG Reel Tracker
            </h1>
            <p className="text-muted-foreground mt-1">
              追蹤 Instagram Reel 數據變化
            </p>
          </div>
          <div className="flex items-center gap-3 pt-1">
            {user === undefined ? null : user ? (
              <>
                <span className="text-sm text-zinc-600">@{user.username}</span>
                <button
                  onClick={handleLogout}
                  className="text-sm px-3 py-1.5 rounded-md border border-zinc-300 hover:bg-zinc-100 transition-colors"
                >
                  登出
                </button>
              </>
            ) : (
              <a
                href="/api/auth/instagram"
                className="text-sm px-4 py-1.5 rounded-md bg-gradient-to-r from-purple-500 to-pink-500 text-white hover:opacity-90 transition-opacity font-medium"
              >
                Instagram 登入
              </a>
            )}
          </div>
        </div>

        <div className="relative">
          <AddVideoForm onAdded={handleAdded} />
        </div>

        {videos.length > 0 && <StatsGrid videos={videos} />}

        {loading ? (
          <p className="text-center text-muted-foreground py-12">載入中...</p>
        ) : videos.length === 0 ? (
          <p className="text-center text-muted-foreground py-12">
            還沒有任何影片，貼上 IG Reel 連結開始追蹤
          </p>
        ) : (
          <div className="space-y-4">
            {videos.map((v) => (
              <VideoCard
                key={v.id}
                video={v}
                onDeleted={handleDeleted}
                onRefreshed={handleRefreshed}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
