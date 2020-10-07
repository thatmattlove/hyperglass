import * as React from 'react';
import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useTheme } from '@chakra-ui/core';
import { useConfig } from 'app/context';
import { googleFontUrl } from 'app/util';

export const Meta = () => {
  const config = useConfig();
  const theme = useTheme();
  const [location, setLocation] = useState({});
  const title = config?.site_title || 'hyperglass';
  const description = config?.site_description || 'Network Looking Glass';
  const siteName = `${title} - ${description}`;
  const keywords = config?.site_keywords || [
    'hyperglass',
    'looking glass',
    'lg',
    'peer',
    'peering',
    'ipv4',
    'ipv6',
    'transit',
    'community',
    'communities',
    'bgp',
    'routing',
    'network',
    'isp',
  ];
  const language = config?.language ?? 'en';
  const primaryFont = googleFontUrl(theme.fonts.body);
  const monoFont = googleFontUrl(theme.fonts.mono);
  useEffect(() => {
    if (typeof window !== 'undefined' && location === {}) {
      setLocation(window.location);
    }
  }, [location]);
  return (
    <Head>
      <title>{title}</title>
      <meta name="hg-version" content={config.hyperglass_version} />
      <meta name="description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />
      <meta name="language" content={language} />
      <meta name="url" content={location.href} />
      <meta name="og:title" content={title} />
      <meta name="og:url" content={location.href} />
      <meta name="og:description" content={description} />
      <meta property="og:image:alt" content={siteName} />
      <link href={primaryFont} rel="stylesheet" />
      <link href={monoFont} rel="stylesheet" />
    </Head>
  );
};
