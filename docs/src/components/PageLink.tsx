import * as React from "react";
import Link from "@docusaurus/Link";

import type { LinkProps } from "@docusaurus/Link";

const PageLink = (props: React.PropsWithChildren<LinkProps>): JSX.Element => {
  return <Link style={{ textDecoration: "unset" }} {...props} />;
};

export default PageLink;
