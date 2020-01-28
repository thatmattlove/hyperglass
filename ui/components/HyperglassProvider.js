import React, { createContext, useContext, useMemo } from "react";
import dynamic from "next/dynamic";
import { CSSReset, ThemeProvider } from "@chakra-ui/core";
import { MediaProvider } from "~/components/MediaProvider";
import { makeTheme, defaultTheme } from "~/theme";

// Disable SSR for ColorModeProvider
const ColorModeProvider = dynamic(
    () => import("@chakra-ui/core").then(mod => mod.ColorModeProvider),
    { ssr: false }
);

const HyperglassContext = createContext(null);

export const HyperglassProvider = ({ config, children }) => {
    const value = useMemo(() => config, [config]);
    const userTheme = value && makeTheme(value.web.theme);
    const theme = value ? userTheme : defaultTheme;
    return (
        <HyperglassContext.Provider value={value}>
            <ThemeProvider theme={theme}>
                <ColorModeProvider>
                    <CSSReset />
                    <MediaProvider theme={theme}>{children}</MediaProvider>
                </ColorModeProvider>
            </ThemeProvider>
        </HyperglassContext.Provider>
    );
};

export default () => useContext(HyperglassContext);
