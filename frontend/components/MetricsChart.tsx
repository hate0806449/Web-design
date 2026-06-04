"use client";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { SnapshotData } from "@/types";

interface Props {
  snapshots: SnapshotData[];
}

function fmtTime(iso: string): string {
  const d = new Date(iso);
  return `${d.getMonth() + 1}/${d.getDate()} ${String(d.getHours()).padStart(
    2,
    "0"
  )}:${String(d.getMinutes()).padStart(2, "0")}`;
}

export function MetricsChart({ snapshots }: Props) {
  if (snapshots.length < 2) {
    return (
      <p className="text-sm text-muted-foreground py-4 text-center">
        需要至少 2 筆快照才能顯示趨勢圖
      </p>
    );
  }

  const data = snapshots.map((s) => ({
    time: fmtTime(s.scrapedAt),
    總觀看: s.views,
    IG觀看: s.igViews,
    按讚: s.likes,
    留言: s.comments,
  }));

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data}>
        <XAxis dataKey="time" tick={{ fontSize: 11 }} />
        <YAxis tick={{ fontSize: 11 }} />
        <Tooltip />
        <Legend />
        <Line type="monotone" dataKey="總觀看" stroke="#6366f1" dot={false} />
        <Line
          type="monotone"
          dataKey="IG觀看"
          stroke="#94a3b8"
          strokeDasharray="3 3"
          dot={false}
        />
        <Line type="monotone" dataKey="按讚" stroke="#ec4899" dot={false} />
        <Line type="monotone" dataKey="留言" stroke="#22c55e" dot={false} />
      </LineChart>
    </ResponsiveContainer>
  );
}