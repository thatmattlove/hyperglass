const githubURL = "https://github.com/checktheroads/hyperglass";

const { googleTrackingId, algoliaKey } = process.env;

const docusaurusConfig = {
  title: "hyperglass",
  tagline: "the network looking glass that tries to make the internet better.",
  url: "https://hyperglass.io",
  baseUrl: "/",
  favicon: "img/favicon.ico",
  organizationName: "checktheroads",
  projectName: "hyperglass",
  themeConfig: {
    image: "opengraph.jpg",
    googleAnalytics: {
      trackingID: googleTrackingId || " ",
      anonymizeIP: false,
    },
    algolia: {
      apiKey: algoliaKey || "dev",
      indexName: "hyperglass",
    },
    prism: {
      additionalLanguages: ["shell-session", "ini", "nginx", "yaml"],
      theme: require("./src/prism-dracula"),
    },
    navbar: {
      items: [
        { to: "docs/introduction", label: "Docs", position: "left" },
        { href: "https://demo.hyperglass.io", label: "Demo", position: "left" },
        {
          href: githubURL,
          position: "right",
          className: "header-github-link",
          "aria-label": "GitHub Repository",
        },
      ],
    },
    footer: {
      links: [
        {
          title: "Docs",
          items: [
            {
              label: "Introduction",
              to: "docs/introduction",
            },
            {
              label: "Getting Started",
              to: "docs/getting-started",
            },
            {
              label: "Configuration",
              to: "docs/parameters",
            },
          ],
        },
        {
          title: "Community",
          items: [
            {
              label: "Slack",
              href: "https://netdev.chat",
            },
            {
              label: "Telegram",
              href: "https://t.me/hyperglasslg",
            },
          ],
        },
        {
          title: "Social",
          items: [
            {
              label: "GitHub",
              href: githubURL,
            },
            {
              label: "Twitter",
              href: "https://twitter.com/checktheroads",
            },
          ],
        },
      ],
    },
  },
  presets: [
    [
      "@docusaurus/preset-classic",
      {
        docs: {
          sidebarPath: require.resolve("./sidebars.js"),
          editUrl: githubURL + "/edit/v1.0.0/docs/",
        },
        theme: {
          customCss: [require.resolve("./src/css/custom.css")],
        },
      },
    ],
  ],
};

module.exports = docusaurusConfig;
