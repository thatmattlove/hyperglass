import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import type { AppProps } from 'next/app';
import { Layout, Meta } from '~/components';
import { HyperglassProvider } from '~/context';
import type { Config } from '~/types';

// Declare imported JSON type to avoid type errors when file is not present (testing).
const config = (await import('../hyperglass.json')) as unknown as Config;

const queryClient = new QueryClient();

const App = (props: AppProps): JSX.Element => {
  const { Component, pageProps } = props;
  return (
    <QueryClientProvider client={queryClient}>
      <HyperglassProvider config={config}>
        <Meta />
        <Layout>
          <Component {...pageProps} />
        </Layout>
      </HyperglassProvider>
    </QueryClientProvider>
  );
};

export default App;
