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
        "parameters",
        "adding-devices",
        "commands",
        "logging",
        "messages",
        "query-settings",
        "response-caching",
        "rest-api",
        "table-output",
        {
          type: "category",
          label: "Web UI",
          items: [
            "ui/configuration",
            "ui/logo",
            "ui/text",
            "ui/theme",
            "ui/example",
          ],
        },
      ],
    },
    {
      type: "category",
      label: "Linux Agent",
      items: ["agent/installation", "agent/setup", "agent/parameters"],
    },
    { type: "doc", id: "production" },
    { type: "doc", id: "upgrading" },
    { type: "doc", id: "platforms" },
    { type: "doc", id: "license" },
  ],
};
