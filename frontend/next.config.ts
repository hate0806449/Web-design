import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // 前端 /api/* 代理到 FastAPI 後端，這樣前端 fetch 都打同源就好
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:8000/api/:path*",
      },
    ];
  },
};

export default nextConfig;
