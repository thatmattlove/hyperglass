const envData = require('/tmp/hyperglass.env.json');

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  env: { ...envData },
  typescript: {
    ignoreBuildErrors: true,
  },
};

module.exports = nextConfig;
