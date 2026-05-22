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
  const snapshots = videos.map((v) => v.latestSnapshot).filter(Boolean);

  const totalViews = snapshots.reduce((s, snap) => s + (snap!.views ?? 0), 0);
  const totalLikes = snapshots.reduce((s, snap) => s + (snap!.likes ?? 0), 0);
  const totalComments = snapshots.reduce(
    (s, snap) => s + (snap!.comments ?? 0),
    0
  );

  const stats = [
    { label: "總觀看數", value: fmt(totalViews), icon: "👁" },
    { label: "總按讚", value: fmt(totalLikes), icon: "❤️" },
    { label: "總留言", value: fmt(totalComments), icon: "💬" },
    { label: "追蹤影片", value: String(videos.length), icon: "🎬" },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {stats.map((s) => (
        <div
          key={s.label}
          className="bg-white rounded-xl border p-4 flex flex-col gap-1"
        >
          <span className="text-2xl">{s.icon}</span>
          <span className="text-2xl font-bold tracking-tight">{s.value}</span>
          <span className="text-sm text-muted-foreground">{s.label}</span>
        </div>
      ))}
    </div>
  );
}
