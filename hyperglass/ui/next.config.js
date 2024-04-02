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
  output: 'export',
};

if (process.env.NODE_ENV === 'development') {
  nextConfig.rewrites = [
    { source: '/api/query', destination: `${process.env.HYPERGLASS_URL}api/query` },
    { source: '/images/:image*', destination: `${process.env.HYPERGLASS_URL}images/:image*` },
  ];
}

module.exports = nextConfig;
