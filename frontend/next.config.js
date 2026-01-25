/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'https://rimshaarshad-todo-app.hf.space',
  },
  images: {
    domains: ['localhost', '0.0.0.0'],
  },
  transpilePackages: [],
};

module.exports = nextConfig;