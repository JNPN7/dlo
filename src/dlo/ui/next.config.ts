import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Static export for FastAPI to serve
  // output: "export",

  // Trailing slashes for static hosting compatibility
  trailingSlash: true,

  // Disable image optimization for static export
  images: {
    unoptimized: true,
  },

  // Note: rewrites only work in development mode with static export
  // In production, FastAPI handles the API proxy
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: "http://localhost:6363/api/:path*",
      },
    ];
  },
};

export default nextConfig;
