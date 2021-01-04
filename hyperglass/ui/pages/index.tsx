import Head from 'next/head';
import dynamic from 'next/dynamic';
import { Meta, Loading } from '~/components';

import type { GetStaticProps } from 'next';
import type { Favicon, FaviconComponent } from '~/types';

const Layout = dynamic<Dict>(() => import('~/components').then(i => i.Layout), {
  loading: Loading,
});

interface TIndex {
  favicons: FaviconComponent[];
}

const Index: React.FC<TIndex> = (props: TIndex) => {
  const { favicons } = props;
  return (
    <>
      <Head>
        {favicons.map((icon, idx) => {
          const { rel, href, type } = icon;
          return <link rel={rel} href={href} type={type} key={idx} />;
        })}
      </Head>
      <Meta />
      <Layout />
    </>
  );
};

export const getStaticProps: GetStaticProps<TIndex> = async () => {
  const faviconConfig = (process.env._HYPERGLASS_FAVICONS_ as unknown) as Favicon[];
  const favicons = faviconConfig.map(icon => {
    const { image_format, dimensions, prefix } = icon;
    let { rel } = icon;
    if (rel === null) {
      rel = '';
    }
    const src = `/images/favicons/${prefix}-${dimensions[0]}x${dimensions[1]}.${image_format}`;
    return { rel, href: src, type: `image/${image_format}` };
  });
  return {
    props: { favicons },
  };
};

export default Index;
