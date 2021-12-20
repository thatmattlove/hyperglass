import { QueryClient, QueryClientProvider } from 'react-query';
import { Switch, Case, Default } from 'react-if';
import { Meta, Layout } from '~/components';
import { HyperglassProvider } from '~/context';
import { LoadError, Loading } from '~/elements';
import { useHyperglassConfig } from '~/hooks';

import type { AppProps } from 'next/app';

const queryClient = new QueryClient();

const AppComponent = (props: AppProps) => {
  const { Component, pageProps } = props;
  const { data, error, isLoading, ready, refetch, showError, isLoadingInitial } =
    useHyperglassConfig();
  return (
    <Switch>
      <Case condition={isLoadingInitial}>
        <Loading />
      </Case>
      <Case condition={showError}>
        <LoadError error={error!} retry={refetch} inProgress={isLoading} />
      </Case>
      <Case condition={ready}>
        <HyperglassProvider config={data!}>
          <Meta />
          <Layout>
            <Component {...pageProps} />
          </Layout>
        </HyperglassProvider>
      </Case>
      <Default>
        <LoadError error={error!} retry={refetch} inProgress={isLoading} />
      </Default>
    </Switch>
  );
};

const App = (props: AppProps): JSX.Element => {
  return (
    <QueryClientProvider client={queryClient}>
      <AppComponent {...props} />
    </QueryClientProvider>
  );
};

export default App;
