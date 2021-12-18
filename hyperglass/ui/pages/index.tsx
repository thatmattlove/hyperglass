import dynamic from 'next/dynamic';
import { Switch, Case, Default } from 'react-if';
import { Meta, Loading, LoadError } from '~/components';
import { HyperglassProvider } from '~/context';
import { useHyperglassConfig } from '~/hooks';

import type { NextPage } from 'next';

const Layout = dynamic<Dict>(() => import('~/components').then(i => i.Layout), {
  loading: Loading,
});

const Index: NextPage = () => {
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
          <Layout />
        </HyperglassProvider>
      </Case>
      <Default>
        <LoadError error={error!} retry={refetch} inProgress={isLoading} />
      </Default>
    </Switch>
  );
};

export default Index;
