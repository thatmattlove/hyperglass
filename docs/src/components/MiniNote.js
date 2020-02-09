import React from "react";

export default ({ children }) => (
    <>
        <br />
        <span
            style={{
                fontSize: "var(--ifm-font-size-sm)",
                color: "var(--ifm-blockquote-color)",
                display: "inline-block",
                fontStyle: "italic"
            }}
        >
            {children}
        </span>
    </>
);
