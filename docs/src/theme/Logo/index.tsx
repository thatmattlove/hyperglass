/**
 * Copyright (c) Facebook, Inc. and its affiliates.
 *
 * This source code is licensed under the MIT license found in the
 * LICENSE file in the root directory of this source tree.
 */

import React from "react";
import type { Props } from "@theme/Logo";

import clsx from "clsx";
import Link from "@docusaurus/Link";
import ThemedImage from "@theme/ThemedImage";
import useBaseUrl from "@docusaurus/useBaseUrl";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";
import { useThemeConfig } from "@docusaurus/theme-common";
import { useLogoSrc } from "../../hooks";

const Logo = (props: Props): JSX.Element => {
  const { sources, className } = useLogoSrc();

  const { isClient } = useDocusaurusContext();
  const {
    navbar: { title, logo = { src: "" } },
  } = useThemeConfig();

  const { imageClassName, titleClassName, ...propsRest } = props;
  const logoLink = useBaseUrl(logo.href || "/");

  return (
    <Link
      to={logoLink}
      {...propsRest}
      {...(logo.target && { target: logo.target })}
    >
      {sources.light && (
        <ThemedImage
          key={isClient}
          className={clsx(imageClassName, className)}
          sources={sources}
          alt={logo.alt || title || "Logo"}
        />
      )}
      {title != null && <strong className={titleClassName}>{title}</strong>}
    </Link>
  );
};

export default Logo;
