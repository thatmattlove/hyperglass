import React from "react";
import { HyperglassProvider } from "~/components/HyperglassProvider";

const config = process.env._HYPERGLASS_CONFIG_;

const Hyperglass = ({ Component, pageProps }) => {
    return (
        <HyperglassProvider config={config}>
            <Component {...pageProps} />
        </HyperglassProvider>
    );
};

Hyperglass.displayName = "Hyperglass";

export default Hyperglass;
