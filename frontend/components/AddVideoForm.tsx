"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
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
    <form onSubmit={handleSubmit} className="relative flex gap-2">
      <Input
        placeholder="貼上 Instagram Reel 連結..."
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        className="flex-1"
        disabled={loading}
      />
      <Button type="submit" disabled={loading || !url.trim()}>
        {loading ? "追蹤中..." : "追蹤"}
      </Button>
      {error && (
        <p className="absolute mt-12 text-sm text-red-500">{error}</p>
      )}
    </form>
  );
}
