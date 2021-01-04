import { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import { useTheme } from '@chakra-ui/react';
import { useConfig } from '~/context';
import { googleFontUrl } from '~/util';

export const Meta: React.FC = () => {
  const config = useConfig();
  const { fonts } = useTheme();
  const [location, setLocation] = useState('/');

  const {
    site_title: title = 'hyperglass',
    site_description: description = 'Network Looking Glass',
    site_keywords: keywords = [
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
    ],
  } = useConfig();

  const siteName = `${title} - ${description}`;
  const primaryFont = useMemo(() => googleFontUrl(fonts.body), []);
  const monoFont = useMemo(() => googleFontUrl(fonts.mono), []);

  useEffect(() => {
    if (typeof window !== 'undefined' && location === '/') {
      setLocation(window.location.href);
    }
  }, []);

  return (
    <Head>
      <title>{title}</title>
      <meta name="language" content="en" />
      <meta name="url" content={location} />
      <meta name="og:title" content={title} />
      <meta name="og:url" content={location} />
      <link href={monoFont} rel="stylesheet" />
      <link href={primaryFont} rel="stylesheet" />
      <meta name="description" content={description} />
      <meta property="og:image:alt" content={siteName} />
      <meta name="og:description" content={description} />
      <meta name="keywords" content={keywords.join(', ')} />
      <meta name="hg-version" content={config.hyperglass_version} />
    </Head>
  );
};
