const withNextra = require('nextra')({
  theme: 'nextra-theme-docs',
  themeConfig: './theme.config.tsx',
});

module.exports = withNextra({
  // experimental: {
  //   runtime: 'experimental-edge',
  // },
  images: {
    unoptimized: true,
  },
});