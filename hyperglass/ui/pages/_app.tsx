import Head from 'next/head';
import { HyperglassProvider } from '~/context';
import { IConfig } from '~/types';
// import { useRouter } from "next/router";
// import Error from "./_error";

import type { AppProps, AppInitialProps } from 'next/app';

type TAppProps = AppProps & AppInitialProps;

interface TApp extends TAppProps {
  appProps: { config: IConfig };
}

type TAppInitial = Pick<TApp, 'appProps'>;

const App = (props: TApp) => {
  const { Component, pageProps, appProps } = props;
  const { config } = appProps;

  // const { asPath } = useRouter();
  // if (asPath === "/structured") {
  //   return <Error msg="/structured" statusCode={404} />;
  // }
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
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </Head>
      <HyperglassProvider config={config}>
        <Component {...pageProps} />
      </HyperglassProvider>
    </>
  );
};

App.getInitialProps = async (): Promise<TAppInitial> => {
  const config = (process.env._HYPERGLASS_CONFIG_ as unknown) as IConfig;
  return { appProps: { config } };
};

export default App;
