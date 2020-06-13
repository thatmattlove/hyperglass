import React, { useEffect, useState } from "react";
import Head from "next/head";
import { useTheme } from "@chakra-ui/core";
import useConfig from "~/components/HyperglassProvider";
import { googleFontUrl } from "~/util";

const Meta = () => {
  const config = useConfig();
  const theme = useTheme();
  const [location, setLocation] = useState({});
  const title = config?.site_title || "hyperglass";
  const description = config?.site_description || "The modern looking glass.";
  const siteName = `${title} - ${description}`;
  const keywords = config?.site_keywords || [
    "hyperglass",
    "looking glass",
    "lg",
    "peer",
    "peering",
    "ipv4",
    "ipv6",
    "transit",
    "community",
    "communities",
    "bgp",
    "routing",
    "network",
    "isp"
  ];
  const language = config?.language ?? "en";
  const ogImage = config?.web.opengraph.image ?? null;
  const ogImageHeight = config?.web.opengraph.height ?? null;
  const ogImageWidth = config?.web.opengraph.width ?? null;
  const primaryFont = googleFontUrl(theme.fonts.body);
  const monoFont = googleFontUrl(theme.fonts.mono);
  useEffect(() => {
    if (typeof window !== undefined && location === {}) {
      setLocation(window.location);
    }
  }, [location]);
  return (
    <Head>
      <title>{title}</title>
      <meta name="hg-version" content={config.hyperglass_version} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(", ")} />
      <meta name="language" content={language} />
      <meta name="url" content={location.href} />
      <meta name="og:title" content={title} />
      <meta name="og:url" content={location.href} />
      <meta name="og:image" content={ogImage} />
      <meta name="og:description" content={description} />
      <meta property="og:image:alt" content={siteName} />
      <meta property="og:image:width" content={ogImageWidth} />
      <meta property="og:image:height" content={ogImageHeight} />
      <link href={primaryFont} rel="stylesheet" />
      <link href={monoFont} rel="stylesheet" />
    </Head>
  );
};

export default Meta;
