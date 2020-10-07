import * as React from 'react';
import Head from 'next/head';
// import { useRouter } from "next/router";
import { HyperglassProvider } from 'app/context';
// import Error from "./_error";

const config = process.env._HYPERGLASS_CONFIG_;

const Hyperglass = ({ Component, pageProps }) => {
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
      </Head>
      <HyperglassProvider config={config}>
        <Component {...pageProps} />
      </HyperglassProvider>
    </>
  );
};

export default Hyperglass;
