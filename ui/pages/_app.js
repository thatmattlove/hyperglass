import React from "react";
import useAxios from "axios-hooks";
import { HyperglassProvider } from "~/components/HyperglassProvider";
import PreConfig from "~/components/PreConfig";

const Hyperglass = ({ Component, pageProps }) => {
    const [{ data, loading, error }, refetch] = useAxios({
        url: "/api/config",
        method: "get"
    });
    return (
        <>
            {!data ? (
                <PreConfig loading={loading} error={error} refresh={refetch} />
            ) : (
                <HyperglassProvider config={data}>
                    <Component {...pageProps} />
                </HyperglassProvider>
            )}
        </>
    );
};

Hyperglass.displayName = "Hyperglass";

export default Hyperglass;
