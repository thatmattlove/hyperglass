import React from "react";

export default ({ children }) => (
    <span
        style={{
            backgroundColor: "var(--ifm-code-background)",
            color: "var(--ifm-code-color)",
            fontFamily: "var(--ifm-font-family-monospace)",
            fontSize: "var(--ifm-code-font-size)",
            borderRadius: "var(--ifm-code-border-radius)",
            margin: 0,
            padding: "var(--ifm-code-padding-vertical) var(--ifm-code-padding-horizontal)"
        }}
    >
        {children}
    </span>
);
