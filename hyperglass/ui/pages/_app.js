import React from "react";
import { useRouter } from "next/router";
import { HyperglassProvider } from "~/components/HyperglassProvider";
import Error from "./_error";

const config = process.env._HYPERGLASS_CONFIG_;

const Hyperglass = ({ Component, pageProps }) => {
  // const { asPath } = useRouter();
  // if (asPath === "/structured") {
  //   return <Error msg="/structured" statusCode={404} />;
  // }
  return (
    <HyperglassProvider config={config}>
      <Component {...pageProps} />
    </HyperglassProvider>
  );
};

Hyperglass.displayName = "Hyperglass";

export default Hyperglass;
