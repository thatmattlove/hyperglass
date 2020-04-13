module.exports = {
    someSidebar: [
        {
            type: "category",
            label: "Installation",
            items: ["introduction", "getting-started", "setup"],
        },
        {
            type: "category",
            label: "Configuration",
            items: [
                "configuration",
                "devices",
                "commands",
                "ui",
                "cache",
                "api",
                "messages",
                "queries",
            ],
        },
        { type: "category", label: "Linux Agent", items: ["agent/installation"] },
        { type: "doc", id: "upgrading" },
        { type: "doc", id: "platforms" },
        { type: "doc", id: "license" },
    ],
};
