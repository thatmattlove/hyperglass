import Head from 'next/head';
import { QueryClient, QueryClientProvider } from 'react-query';

import type { AppProps } from 'next/app';

if (process.env.NODE_ENV === 'development') {
  require('@hookstate/devtools');
}

const queryClient = new QueryClient();

const App = (props: AppProps): JSX.Element => {
  const { Component, pageProps } = props;

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
      <QueryClientProvider client={queryClient}>
        <Component {...pageProps} />
      </QueryClientProvider>
    </>
  );
};

export default App;
