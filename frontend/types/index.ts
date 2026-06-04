export interface SnapshotData {
  id: string;
  videoId: string;
  views: number | null;
  igViews: number | null;
  fbViews: number | null;
  likes: number | null;
  comments: number | null;
  shares: number | null;
  scrapedAt: string;
}

export interface VideoWithLatestSnapshot {
  id: string;
  shortcode: string;
  mediaId: string | null;
  username: string | null;
  caption: string | null;
  uploadedAt: string | null;
  createdAt: string;
  latestSnapshot: SnapshotData | null;
}

export interface VideoWithSnapshots extends VideoWithLatestSnapshot {
  snapshots: SnapshotData[];
}

export interface IgUser {
  id: string;
  username: string;
}

export interface ReelData {
  id: string;
  shortcode: string;
  caption: string;
  timestamp: string;
  permalink: string;
  thumbnailUrl: string | null;
  plays: number | null;
  igViews: number | null;
  fbViews: number | null;
  likes: number | null;
  comments: number | null;
  shares: number | null;
}