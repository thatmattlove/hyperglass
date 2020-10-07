import * as React from 'react';
import Head from 'next/head';
import dynamic from 'next/dynamic';
import { Meta, Loading } from 'app/components';
const LookingGlass = dynamic(
  () => import('app/components/LookingGlass').then(i => i.LookingGlass),
  {
    loading: Loading,
  },
);

const Index = ({ faviconComponents }) => {
  return (
    <>
      <Head>
        {faviconComponents.map(({ rel, href, type }, i) => (
          <link rel={rel} href={href} type={type} key={i} />
        ))}
      </Head>
      <Meta />
      <LookingGlass />
    </>
  );
};

export async function getStaticProps(context) {
  const components = process.env._HYPERGLASS_FAVICONS_.map(icon => {
    const { image_format, dimensions, prefix, rel } = icon;
    const src = `/images/favicons/${prefix}-${dimensions[0]}x${dimensions[1]}.${image_format}`;
    return { rel, href: src, type: `image/${image_format}` };
  });
  return {
    props: {
      faviconComponents: components,
    },
  };
}

export default Index;
