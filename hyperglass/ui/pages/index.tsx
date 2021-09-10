import Head from 'next/head';
import dynamic from 'next/dynamic';
import { Meta, Loading, If, LoadError } from '~/components';
import { HyperglassProvider } from '~/context';
import { useHyperglassConfig } from '~/hooks';
import { getFavicons } from '~/util';

import type { GetStaticProps } from 'next';
import type { FaviconComponent } from '~/types';

const Layout = dynamic<Dict>(() => import('~/components').then(i => i.Layout), {
  loading: Loading,
});

interface TIndex {
  favicons: FaviconComponent[];
}

const Index = (props: TIndex): JSX.Element => {
  const { favicons } = props;
  const { data, error, isLoading, ready, refetch, showError, isLoadingInitial } =
    useHyperglassConfig();

  return (
    <>
      <Head>
        {favicons.map((icon, idx) => {
          const { rel, href, type } = icon;
          return <link rel={rel} href={href} type={type} key={idx} />;
        })}
      </Head>
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

export const getStaticProps: GetStaticProps<TIndex> = async () => {
  const favicons = await getFavicons();
  return {
    props: { favicons },
  };
};

export default Index;
