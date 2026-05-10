"use client";

import { useState } from "react";
import { VideoWithLatestSnapshot } from "@/types";

interface Props {
  onAdded: (video: VideoWithLatestSnapshot) => void;
}

export function AddVideoForm({ onAdded }: Props) {
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!url.trim()) return;
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/videos", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "新增失敗");
      onAdded(data);
      setUrl("");
    } catch (err) {
      setError(String(err instanceof Error ? err.message : err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} style={{ marginBottom: 12 }}>
      <input
        type="text"
        placeholder="貼上 Instagram Reel 連結..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        disabled={loading}
        style={{ width: 320, padding: 6 }}
      />
      <button type="submit" disabled={loading || !url.trim()} style={{ padding: "6px 12px", marginLeft: 6 }}>
        {loading ? "追蹤中..." : "追蹤"}
      </button>
      {error && <p style={{ color: "red", fontSize: 12 }}>{error}</p>}
    </form>
  );
}
