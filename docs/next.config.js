const fs = require("node:fs");
const path = require("node:path");

function copyChangelog() {
    const src = path.resolve(__dirname, "..", "CHANGELOG.md");
    const data = fs.readFileSync(src);
    const replaced = data.toString().replace("# Changelog\n\n", "");
    const dst = path.resolve(__dirname, "pages", "changelog.mdx");
    fs.writeFileSync(dst, replaced);
}

copyChangelog();

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
