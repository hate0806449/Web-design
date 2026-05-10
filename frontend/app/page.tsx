"use client";

import { useEffect, useState } from "react";
import { AddVideoForm } from "@/components/AddVideoForm";
import { StatsGrid } from "@/components/StatsGrid";
import { VideoWithLatestSnapshot, IgUser } from "@/types";

function fmt(n: number | null): string {
  if (n == null) return "-";
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

export default function Home() {
  const [videos, setVideos] = useState<VideoWithLatestSnapshot[]>([]);
  const [user, setUser] = useState<IgUser | null | undefined>(undefined);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("/api/videos")
      .then((r) => r.json())
      .then((data) => setVideos(data))
      .catch((e) => console.error("load videos fail", e))
      .finally(() => setLoading(false));

    fetch("/api/auth/me")
      .then((r) => r.json())
      .then((data) => setUser(data ?? null));
  }, []);

  function handleAdded(v: VideoWithLatestSnapshot) {
    setVideos((prev) => [v, ...prev]);
  }

  async function handleLogout() {
    await fetch("/api/auth/logout", { method: "POST" });
    setUser(null);
  }

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1>IG Reel Tracker</h1>
        <div>
          {user === undefined ? null : user ? (
            <>
              <span style={{ marginRight: 8 }}>@{user.username}</span>
              <button onClick={handleLogout}>登出</button>
            </>
          ) : (
            <a href="/api/auth/instagram">Instagram 登入</a>
          )}
        </div>
      </div>
      <p>追蹤 Instagram Reel 數據變化</p>

      <hr />

      <AddVideoForm onAdded={handleAdded} />

      {videos.length > 0 && <StatsGrid videos={videos} />}

      <hr />

      <h2>追蹤清單</h2>
      {loading ? (
        <p>載入中...</p>
      ) : videos.length === 0 ? (
        <p>還沒有任何影片，貼上 IG Reel 連結開始追蹤</p>
      ) : (
        <ul>
          {videos.map((v) => {
            const s = v.latestSnapshot;
            return (
              <li key={v.id}>
                <b>@{v.username ?? "unknown"}</b> ({v.shortcode}) — 觀看 {fmt(s?.views ?? null)}
                {s?.igViews != null && s.igViews !== s.views && (
                  <span style={{ color: "#888", fontSize: 11 }}>
                    {" "}(IG {fmt(s.igViews)} / FB {fmt(s.fbViews)})
                  </span>
                )}
                {" "}/ 讚 {fmt(s?.likes ?? null)} / 留言 {fmt(s?.comments ?? null)}
              </li>
            );
          })}
        </ul>
      )}

      <hr />
      <p style={{ color: "gray", fontSize: 12 }}>
        v0.2 / 接 DB + IG 真實數據 / UI 還醜，下週給穎禾美化
      </p>
    </div>
  );
}
