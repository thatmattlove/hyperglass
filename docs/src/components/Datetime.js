import React from "react";

export default ({ year = false, ...props }) => {
    const date = new Date();
    const granularity = year ? date.getFullYear() : date.toString();
    return <span {...props}>{granularity}</span>;
};
