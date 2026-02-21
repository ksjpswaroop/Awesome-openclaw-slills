/** @type {import('next').NextConfig} */
const nextConfig = {
  // Allow loading registry from parent skills_index
  async rewrites() {
    return [];
  },
};

module.exports = nextConfig;
