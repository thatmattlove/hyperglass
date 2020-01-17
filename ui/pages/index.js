import React from "react";
import dynamic from "next/dynamic";
import useAxios from "axios-hooks";
import { CSSReset, ThemeProvider } from "@chakra-ui/core";
import Layout from "~/components/Layout";
import PreConfig from "~/components/PreConfig";
import { makeTheme, defaultTheme } from "~/theme";

// Disable SSR for ColorModeProvider
const ColorModeProvider = dynamic(
    () => import("@chakra-ui/core").then(mod => mod.ColorModeProvider),
    { ssr: false }
);

const Index = () => {
    const [{ data, loading, error }, refetch] = useAxios({
        url: "/config",
        method: "get"
    });
    // const data = undefined;
    // const loading = false;
    // const error = { message: "Shit broke" };
    // const refetch = () => alert("refetched");
    const userTheme = data && makeTheme(data.branding);
    return (
        <ThemeProvider theme={data ? userTheme : defaultTheme}>
            <ColorModeProvider>
                <CSSReset />
                {!data ? (
                    <PreConfig loading={loading} error={error} refresh={refetch} />
                ) : (
                    <Layout config={data} />
                )}
            </ColorModeProvider>
        </ThemeProvider>
    );
};

export default Index;
