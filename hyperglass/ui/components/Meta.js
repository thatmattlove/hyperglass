import React, { useEffect, useState } from "react";
import Head from "next/head";
import { useTheme } from "@chakra-ui/core";
import useConfig from "~/components/HyperglassProvider";
import { googleFontUrl } from "~/util";

export default () => {
    const config = useConfig();
    const theme = useTheme();
    const [location, setLocation] = useState({});
    const title = config?.org_name || "hyperglass";
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
    const author = config?.org_name || "Matt Love, matt@hyperglass.io";
    const language = config?.language || "en";
    const currentYear = new Date().getFullYear();
    const copyright = config ? `${currentYear} ${config.org_name}` : `${currentYear} hyperglass`;
    const ogImage = config?.web.opengraph.image || null;
    const ogImageHeight = config?.web.opengraph.height || null;
    const ogImageWidth = config?.web.opengraph.width || null;
    const primaryFont = googleFontUrl(theme.fonts.body);
    const monoFont = googleFontUrl(theme.fonts.mono);
    useEffect(() => {
        setLocation(window.location);
    });
    return (
        <Head>
            <title>{title}</title>
            <meta charSet="UTF-8" />
            <meta httpEquiv="Content-Type" content="text/html" />
            <meta name="description" content={description} />
            <meta name="keywords" content={keywords.join(", ")} />
            <meta name="author" content={author} />
            <meta name="language" content={language} />
            <meta name="copyright" content={copyright} />
            <meta name="url" content={location.href} />
            <meta name="og:title" content={title} />
            <meta name="og:type" content="website" />
            <meta name="og:site_name" content={siteName} />
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
