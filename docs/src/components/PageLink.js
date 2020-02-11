import React from "react";
import Link from "@docusaurus/Link";

export default ({ children, to }) => (
    <Link to={to} style={{ textDecoration: "unset" }}>
        {children}
    </Link>
);
