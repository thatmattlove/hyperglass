const githubURL = "https://github.com/checktheroads/hyperglass";

module.exports = {
    title: "hyperglass",
    tagline: "documentation for the modern network looking glass",
    url: "https://hyperglass.io",
    baseUrl: "/",
    favicon: "img/favicon.ico",
    organizationName: "checktheroads",
    projectName: "hyperglass",
    themeConfig: {
        navbar: {
            title: "hyperglass",
            logo: {
                alt: "hyperglass icon",
                src: "img/icon.svg"
            },
            links: [
                { to: "docs/introduction", label: "Docs", position: "left" },
                { to: "screenshots", label: "Screenshots", position: "left" },
                {
                    href: "https://demo.hyperglass.io",
                    label: "Demo",
                    position: "left"
                },
                {
                    href: githubURL,
                    label: "GitHub",
                    position: "right"
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
                            label: "Style Guide",
                            to: "docs/getting-started"
                        }
                    ]
                },
                {
                    title: "Community",
                    items: [
                        {
                            label: "Stack Overflow",
                            href: "https://stackoverflow.com/questions/tagged/docusaurus"
                        },
                        {
                            label: "Discord",
                            href: "https://discordapp.com/invite/docusaurus"
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
    ]
};
