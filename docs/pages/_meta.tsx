export default {
    index: { title: "Introduction", theme: { breadcrumb: false } },
    "---": {
        type: "separator",
    },
    installation: "Installation",
    configuration: "Configuration",
    platforms: "Platforms",
    plugins: "Plugins",
    documentation: {
        title: "Documentation",
        type: "menu",
        items: {
            installation: {
                title: "Installation",
                href: "/installation",
            },
            configuration: {
                title: "Configuration",
                href: "/configuration",
            },
            plugins: {
                title: "Plugins",
                href: "/plugins",
            },
            changelog: {
                title: "Changelog",
                href: "/changelog",
            },
            license: {
                title: "License",
                href: "/license",
            },
        },
    },
    demo: {
        title: "Demo",
        type: "page",
        href: "https://demo.hyperglass.dev",
        newWindow: true,
    },
};
