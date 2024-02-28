const rewrites = async () => {
  if (process.env.NODE_ENV === 'production') {
    return [];
  }
  return [
    { source: '/api/query', destination: `${process.env.HYPERGLASS_URL}api/query` },
    { source: '/images/:image*', destination: `${process.env.HYPERGLASS_URL}images/:image*` },
  ];
};

/**
 * @type {import('next').NextConfig}
 */
const nextConfig = {
  reactStrictMode: true,
  poweredByHeader: false,
  typescript: {
    ignoreBuildErrors: true,
  },
  swcMinify: true,
  productionBrowserSourceMaps: true,
  rewrites,
};

module.exports = nextConfig;
