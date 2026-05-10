"use client";

import { VideoWithLatestSnapshot } from "@/types";

function fmt(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return String(n);
}

interface Props {
  videos: VideoWithLatestSnapshot[];
}

export function StatsGrid({ videos }: Props) {
  const snaps = videos.map((v) => v.latestSnapshot).filter(Boolean);

  const totalViews = snaps.reduce((s, sn) => s + (sn!.views ?? 0), 0);
  const totalLikes = snaps.reduce((s, sn) => s + (sn!.likes ?? 0), 0);
  const totalComments = snaps.reduce((s, sn) => s + (sn!.comments ?? 0), 0);

  const items = [
    { label: "總觀看數", value: fmt(totalViews) },
    { label: "總按讚", value: fmt(totalLikes) },
    { label: "總留言", value: fmt(totalComments) },
    { label: "追蹤影片", value: String(videos.length) },
  ];

  return (
    <div
      style={{
        display: "grid",
        gridTemplateColumns: "repeat(4, 1fr)",
        gap: 8,
        margin: "12px 0",
      }}
    >
      {items.map((it) => (
        <div
          key={it.label}
          style={{
            border: "1px solid #ccc",
            padding: 12,
            borderRadius: 4,
            background: "#fafafa",
          }}
        >
          <div style={{ fontSize: 11, color: "#666" }}>{it.label}</div>
          <div style={{ fontSize: 20, fontWeight: 700 }}>{it.value}</div>
        </div>
      ))}
    </div>
  );
}
