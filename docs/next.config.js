const withNextra = require("nextra")({
    theme: "nextra-theme-docs",
    themeConfig: "./theme.config.tsx",
});

/**
 * @type {import('next').NextConfig}
 */
const config = {
    images: {
        unoptimized: true,
    },
    output: "export",
};

module.exports = withNextra(config);
