"use client";

import { useEffect, useState } from "react";
import { ReelData } from "@/types";

function fmt(n: number | null) {
  if (n === null) return "—";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toLocaleString();
}

function timeAgo(ts: string) {
  const diff = (Date.now() - new Date(ts).getTime()) / 1000;
  if (diff < 3600) return `${Math.floor(diff / 60)} 分鐘前`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} 小時前`;
  if (diff < 86400 * 30) return `${Math.floor(diff / 86400)} 天前`;
  return new Date(ts).toLocaleDateString("zh-TW");
}

export function ReelsList() {
  const [reels, setReels] = useState<ReelData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/reels")
      .then((r) => r.json())
      .then((data) => {
        if (data.error) {
          setError(data.error);
        } else {
          setReels(data);
        }
      })
      .catch(() => setError("無法載入"))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <p className="text-center text-muted-foreground py-8">
        載入 Reels 中...
      </p>
    );
  }

  if (error) {
    return <p className="text-center text-red-500 py-8">錯誤：{error}</p>;
  }

  if (reels.length === 0) {
    return (
      <p className="text-center text-muted-foreground py-8">找不到 Reels</p>
    );
  }

  return (
    <div className="space-y-3">
      <h2 className="text-lg font-semibold">
        你的 Reels（最近 {reels.length} 支）
      </h2>
      {reels.map((reel) => (
        <a
          key={reel.id}
          href={reel.permalink}
          target="_blank"
          rel="noopener noreferrer"
          className="flex gap-4 p-4 bg-white rounded-xl border border-zinc-200 hover:border-zinc-300 transition-colors"
        >
          <div className="w-16 h-16 flex-shrink-0 rounded-lg bg-zinc-100 overflow-hidden">
            {reel.thumbnailUrl ? (
              <img
                src={reel.thumbnailUrl}
                alt=""
                className="w-full h-full object-cover"
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-zinc-400 text-xs">
                🎬
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0">
            <p className="text-xs text-zinc-400 mb-1">{timeAgo(reel.timestamp)}</p>
            <p className="text-sm text-zinc-700 line-clamp-2 leading-snug">
              {reel.caption || "（無說明）"}
            </p>

            <div className="flex flex-wrap gap-4 mt-2 text-sm">
              <span className="text-zinc-500">
                <span className="font-semibold text-zinc-800">
                  {fmt(reel.plays)}
                </span>{" "}
                總播放
              </span>
              {reel.igViews !== null && (
                <span className="text-zinc-400 text-xs pt-0.5">
                  IG {fmt(reel.igViews)} / FB {fmt(reel.fbViews)}
                </span>
              )}
              <span className="text-zinc-500">
                <span className="font-semibold text-zinc-800">
                  {fmt(reel.likes)}
                </span>{" "}
                愛心
              </span>
              <span className="text-zinc-500">
                <span className="font-semibold text-zinc-800">
                  {fmt(reel.comments)}
                </span>{" "}
                留言
              </span>
            </div>
          </div>
        </a>
      ))}
    </div>
  );
}