import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Meta, Layout } from '~/components';
import { HyperglassProvider } from '~/context';
import * as config from '../hyperglass.json';

import type { AppProps } from 'next/app';
import type { Config } from '~/types';

const queryClient = new QueryClient();

const App = (props: AppProps): JSX.Element => {
  const { Component, pageProps } = props;
  return (
    <QueryClientProvider client={queryClient}>
      <HyperglassProvider config={config as unknown as Config}>
        <Meta />
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </HyperglassProvider>
    </QueryClientProvider>
  );
};

export default App;
