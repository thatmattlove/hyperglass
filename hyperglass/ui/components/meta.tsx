import { useEffect, useState } from 'react';
import Head from 'next/head';
import { useConfig } from '~/context';

export const Meta = (): JSX.Element => {
  const config = useConfig();
  const [location, setLocation] = useState('/');

  const {
    siteTitle: title = 'hyperglass',
    siteDescription: description = 'Network Looking Glass',
  } = useConfig();

  const siteName = `${title} - ${description}`;

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
      <meta name="description" content={description} />
      <meta property="og:image:alt" content={siteName} />
      <meta name="og:description" content={description} />
      <meta name="hyperglass-version" content={config.version} />
      <meta
        name="viewport"
        content="width=device-width, initial-scale=1, user-scalable=no, maximum-scale=1.0, minimum-scale=1.0"
      />
    </Head>
  );
};
