// @flow

export default {
  plain: {
    color: "rgb(241, 250, 140)",
    backgroundColor: "#282A36",
  },
  styles: [
    {
      types: ["boolean", "number"],
      style: {
        color: "rgb(189, 147, 249)",
      },
    },
    {
      types: [
        "inserted",
        "selector",
        "attr-name",
        "char",
        "builtin",
        "inserted",
        "function",
      ],
      style: {
        color: "rgb(80, 250, 123)",
      },
    },
    {
      types: ["deleted"],
      style: {
        color: "rgb(255, 85, 85)",
      },
    },
    {
      types: ["regex"],
      style: {
        color: "rgb(255, 184, 108)",
      },
    },
    {
      types: ["operator", "entity", "url", "variable"],
      style: {
        color: "rgb(248, 248, 242)",
      },
    },
    {
      types: [
        "constant",
        "tag",
        "selector",
        "shell-symbol",
        "symbol",
        "deleted",
        "punctuation",
      ],
      style: {
        color: "rgb(255, 121, 198)",
      },
    },
    {
      types: ["atrule", "property", "language-bash"],
      style: { color: "rgb(139, 233, 253)" },
    },
    {
      types: ["keyword"],
      style: {
        color: "rgb(139, 233, 253)",
        fontStyle: "italic",
      },
    },
    { types: ["entity"], style: { cursor: "help" } },
    {
      types: ["bold"],
      style: {
        fontStyle: "bold",
      },
    },
    {
      types: ["comment", "output"],
      style: {
        color: "rgb(98, 114, 164)",
      },
    },
    {
      types: ["attr-value", "class-name", "string"],
      style: {
        color: "rgb(241, 250, 140)",
      },
    },
  ],
};
