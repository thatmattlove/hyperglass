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
  experimental: {
    // See: https://github.com/react-hook-form/resolvers/issues/271#issuecomment-986618265
    // See: https://github.com/vercel/next.js/issues/30750#issuecomment-962198711
    esmExternals: false,
  },
};

module.exports = nextConfig;
