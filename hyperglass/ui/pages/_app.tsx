import { useEffect } from 'react';
import Head from 'next/head';
import { HyperglassProvider } from '~/context';
import { useGoogleAnalytics } from '~/hooks';
import { IConfig } from '~/types';

import type { AppProps, AppInitialProps, AppContext } from 'next/app';

if (process.env.NODE_ENV === 'development') {
  require('@hookstate/devtools');
}

type TApp = { config: IConfig };

type GetInitialPropsReturn<IP> = AppProps & AppInitialProps & { appProps: IP };

type NextApp<IP> = React.FC<GetInitialPropsReturn<IP>> & {
  getInitialProps(c?: AppContext): Promise<{ appProps: IP }>;
};

const App: NextApp<TApp> = (props: GetInitialPropsReturn<TApp>) => {
  const { Component, pageProps, appProps, router } = props;
  const { config } = appProps;
  const { initialize, trackPage } = useGoogleAnalytics();

  initialize(config.google_analytics, config.developer_mode);

  useEffect(() => {
    router.events.on('routeChangeComplete', trackPage);
  }, []);

  return (
    <>
      <Head>
        <title>hyperglass</title>
        <meta httpEquiv="Content-Type" content="text/html" />
        <meta charSet="UTF-8" />
        <meta name="og:type" content="website" />
        <meta name="og:image" content="/images/opengraph.jpg" />
        <meta property="og:image:width" content="1200" />
        <meta property="og:image:height" content="630" />
        <meta
          name="viewport"
          content="width=device-width, initial-scale=1, user-scalable=no, maximum-scale=1.0, minimum-scale=1.0"
        />
      </Head>
      <HyperglassProvider config={config}>
        <Component {...pageProps} />
      </HyperglassProvider>
    </>
  );
};

App.getInitialProps = async function getInitialProps() {
  const config = (process.env._HYPERGLASS_CONFIG_ as unknown) as IConfig;
  return { appProps: { config } };
};

export default App;
