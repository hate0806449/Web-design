"use client";

import { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { VideoWithLatestSnapshot } from "@/types";

function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 60) return `${m} 分鐘前`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h} 小時前`;
  return `${Math.floor(h / 24)} 天前`;
}

function fmt(n: number | null): string {
  if (n == null) return "-";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

interface Props {
  video: VideoWithLatestSnapshot;
  onDeleted: (id: string) => void;
  onRefreshed: (video: VideoWithLatestSnapshot) => void;
}

export function VideoCard({ video, onDeleted, onRefreshed }: Props) {
  const [refreshing, setRefreshing] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const snap = video.latestSnapshot;

  async function handleRefresh() {
    setRefreshing(true);
    try {
      await fetch(`/api/videos/${video.id}/refresh`, { method: "POST" });
      const res = await fetch("/api/videos");
      const all: VideoWithLatestSnapshot[] = await res.json();
      const updated = all.find((v) => v.id === video.id);
      if (updated) onRefreshed(updated);
    } finally {
      setRefreshing(false);
    }
  }

  async function handleDelete() {
    if (!confirm(`確定要刪除 @${video.username} 的這部影片嗎？`)) return;
    setDeleting(true);
    await fetch(`/api/videos/${video.id}`, { method: "DELETE" });
    onDeleted(video.id);
  }

  return (
    <Card className="overflow-hidden">
      <CardContent className="p-4">
        <div className="flex gap-4">
          <a
            href={`https://www.instagram.com/reel/${video.shortcode}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="shrink-0"
          >
            <div className="w-20 h-20 bg-gradient-to-br from-purple-400 to-pink-400 rounded-lg flex items-center justify-center text-white text-2xl font-bold">
              IG
            </div>
          </a>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-2">
              <div>
                <p className="font-semibold truncate">
                  @{video.username ?? "unknown"}
                </p>
                {video.caption && (
                  <p className="text-sm text-muted-foreground line-clamp-1">
                    {video.caption}
                  </p>
                )}
              </div>
              <Button
                variant="ghost"
                size="sm"
                className="text-red-400 hover:text-red-600 shrink-0"
                onClick={handleDelete}
                disabled={deleting}
              >
                ✕
              </Button>
            </div>

            <div className="flex flex-wrap items-center gap-2 mt-2">
              <div className="flex items-center">
                <Badge
                  variant="secondary"
                  title="總觀看次數 (包含 Facebook)"
                >
                  👁 {fmt(snap?.views ?? null)}
                </Badge>
                {snap?.igViews != null && snap.igViews !== snap.views && (
                  <span
                    className="text-[10px] text-muted-foreground ml-1"
                    title="純 Instagram 播放次數"
                  >
                    (IG: {fmt(snap.igViews)})
                  </span>
                )}
              </div>
              <Badge variant="secondary">❤️ {fmt(snap?.likes ?? null)}</Badge>
              <Badge variant="secondary">💬 {fmt(snap?.comments ?? null)}</Badge>
            </div>

            <div className="flex items-center justify-between mt-3">
              <span className="text-xs text-muted-foreground">
                {snap ? `更新：${timeAgo(snap.scrapedAt)}` : "尚無數據"}
              </span>
              <Button
                size="sm"
                variant="outline"
                onClick={handleRefresh}
                disabled={refreshing}
              >
                {refreshing ? "刷新中..." : "刷新"}
              </Button>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
