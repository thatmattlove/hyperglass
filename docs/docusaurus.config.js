const githubURL = "https://github.com/checktheroads/hyperglass";

const { googleTrackingId, algoliaKey } = process.env;

module.exports = {
    title: "hyperglass",
    tagline: "the network looking glass that tries to make the internet better.",
    url: "https://hyperglass.io",
    baseUrl: "/",
    favicon: "img/favicon.ico",
    organizationName: "checktheroads",
    projectName: "hyperglass",
    themeConfig: {
        googleAnalytics: { trackingID: googleTrackingId || " ", anonymizeIP: false },
        gtag: {
            trackingID: googleTrackingId || " ",
            anonymizeIP: false
        },
        algolia: {
            apiKey: algoliaKey,
            indexName: "BH4D9OD16A"
        },
        navbar: {
            links: [
                { to: "docs/introduction", label: "Docs", position: "left" },
                { to: "screenshots", label: "Screenshots", position: "left" },
                {
                    href: "https://demo.hyperglass.io",
                    label: "Demo",
                    position: "left"
                }
            ]
        },
        footer: {
            style: "dark",
            links: [
                {
                    title: "Docs",
                    items: [
                        {
                            label: "Introduction",
                            to: "docs/introduction"
                        },
                        {
                            label: "Getting Started",
                            to: "docs/getting-started"
                        },
                        {
                            label: "Configuration",
                            to: "docs/configuration"
                        }
                    ]
                },
                {
                    title: "Community",
                    items: [
                        {
                            label: "Gitter",
                            href: "https://gitter.im/hyperglass"
                        },
                        {
                            label: "Keybase",
                            href: "https://keybase.io/team/hyperglass"
                        }
                    ]
                },
                {
                    title: "Social",
                    items: [
                        {
                            label: "GitHub",
                            href: githubURL
                        },
                        {
                            label: "Twitter",
                            href: "https://twitter.com/checktheroads"
                        }
                    ]
                }
            ]
        }
    },
    presets: [
        [
            "@docusaurus/preset-classic",
            {
                docs: {
                    sidebarPath: require.resolve("./sidebars.js"),
                    editUrl: githubURL + "/edit/master/docs/"
                },
                theme: {
                    customCss: require.resolve("./src/css/custom.css")
                }
            }
        ]
    ],
    plugins: [
        "@docusaurus/plugin-google-analytics",
        "@docusaurus/plugin-google-gtag",
        "@docusaurus/plugin-sitemap"
    ]
};
