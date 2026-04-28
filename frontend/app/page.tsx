"use client";

import { useEffect, useState } from "react";

// 後端假資料的型別
interface Video {
  id: string;
  shortcode: string;
  username: string;
  views: number;
  likes: number;
  comments: number;
}

const API_BASE = "http://localhost:8000";

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([]);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE}/api/videos`)
      .then((r) => r.json())
      .then((data) => setVideos(data))
      .catch((e) => console.error("load fail", e))
      .finally(() => setLoading(false));
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url) return;
    const res = await fetch(`${API_BASE}/api/videos`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });
    const data = await res.json();
    setVideos([data, ...videos]);
    setUrl("");
  }

  return (
    <div>
      <h1>IG Reel Tracker</h1>
      <p>追蹤 Instagram Reel 數據變化</p>

      <p>
        <a href={`${API_BASE}/api/auth/instagram`}>Instagram 登入</a>
      </p>

      <hr />

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="貼上 IG Reel 連結"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          style={{ width: "300px" }}
        />
        <button type="submit">追蹤</button>
      </form>

      <hr />

      <h2>追蹤清單</h2>
      {loading ? (
        <p>載入中...</p>
      ) : videos.length === 0 ? (
        <p>還沒有任何影片</p>
      ) : (
        <ul>
          {videos.map((v) => (
            <li key={v.id}>
              <b>@{v.username}</b> ({v.shortcode}) — 觀看 {v.views} / 讚 {v.likes} / 留言 {v.comments}
            </li>
          ))}
        </ul>
      )}

      <hr />
      <p style={{ color: "gray", fontSize: "12px" }}>
        v0.1 / 假資料版 / UI 之後再優化
      </p>
    </div>
  );
}
