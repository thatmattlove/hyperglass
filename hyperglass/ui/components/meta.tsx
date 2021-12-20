import { useEffect, useMemo, useState } from 'react';
import Head from 'next/head';
import { useConfig } from '~/context';
import { useTheme } from '~/hooks';
import { googleFontUrl } from '~/util';

export const Meta = (): JSX.Element => {
  const config = useConfig();
  const { fonts } = useTheme();
  const [location, setLocation] = useState('/');

  const {
    siteTitle: title = 'hyperglass',
    siteDescription: description = 'Network Looking Glass',
  } = useConfig();

  const siteName = `${title} - ${description}`;
  const primaryFont = useMemo(() => googleFontUrl(fonts.body), [fonts.body]);
  const monoFont = useMemo(() => googleFontUrl(fonts.mono), [fonts.mono]);

  useEffect(() => {
    if (typeof window !== 'undefined' && location === '/') {
      setLocation(window.location.href);
    }
  }, [location]);

  return (
    <Head>
      <title key="title">{title}</title>
      <meta name="url" content={location} />
      <meta name="og:title" content={title} />
      <meta name="og:url" content={location} />
      <link href={monoFont} rel="stylesheet" />
      <link href={primaryFont} rel="stylesheet" />
      <meta name="description" content={description} />
      <meta property="og:image:alt" content={siteName} />
      <meta name="og:description" content={description} />
      <meta name="hyperglass-version" content={config.version} />
    </Head>
  );
};
