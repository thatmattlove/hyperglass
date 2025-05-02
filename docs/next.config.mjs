import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import withNextra from "nextra";

function copyChangelog() {
    const dir = path.dirname(fileURLToPath(import.meta.url));
    const src = path.resolve(dir, "..", "CHANGELOG.md");
    const data = fs.readFileSync(src);
    const replaced = data.toString().replace("# Changelog\n\n", "");
    const dst = path.resolve(dir, "pages", "changelog.mdx");
    fs.writeFileSync(dst, replaced);
}

copyChangelog();

/**
 * @type {import('nextra').NextraConfig}
 */
const nextraConfig = {
    theme: "nextra-theme-docs",
    themeConfig: "./theme.config.tsx",
};

/**
 * @type {import('next').NextConfig}
 */
const config = {
    images: {
        unoptimized: true,
    },
    output: "export",
};

export default withNextra(nextraConfig)(config);
