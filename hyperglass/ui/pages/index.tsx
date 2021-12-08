import dynamic from 'next/dynamic';
import { Meta, Loading, If, LoadError } from '~/components';
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
    <>
      <If c={isLoadingInitial}>
        <Loading />
      </If>
      <If c={showError}>
        <LoadError error={error!} retry={refetch} inProgress={isLoading} />
      </If>
      <If c={ready}>
        <HyperglassProvider config={data!}>
          <Meta />
          <Layout />
        </HyperglassProvider>
      </If>
    </>
  );
};

export default Index;
