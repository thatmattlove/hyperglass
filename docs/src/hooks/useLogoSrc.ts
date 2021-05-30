import { useMemo } from "react";
import useBaseUrl from "@docusaurus/useBaseUrl";
import { useLocation } from "@docusaurus/router";
import useMedia from "use-media";

type UseLogoSrc = {
  sources: { light: string; dark: string };
  className: string | null;
};

export function useLogoSrc(): UseLogoSrc {
  let className = null;
  const { pathname } = useLocation();
  const isSmall = useMedia({ maxWidth: "997px" });
  if (pathname === "/") {
    className = "logo-at-home";
  }
  const sourcesIcon = {
    light: useBaseUrl("/static/hyperglass-icon-light.svg"),
    dark: useBaseUrl("/static/hyperglass-icon-dark.svg"),
  };

  const sourcesFull = {
    light: useBaseUrl("/static/hyperglass-light.svg"),
    dark: useBaseUrl("/static/hyperglass-dark.svg"),
  };

  const sources = useMemo(() => {
    if (isSmall) {
      return sourcesFull;
    }
    if (!isSmall && pathname === "/") {
      return sourcesIcon;
    }
    return sourcesFull;
  }, [isSmall, pathname]);
  return { sources, className };
}
