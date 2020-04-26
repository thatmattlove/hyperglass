import * as React from "react";
import { createContext, useContext, useMemo, useState } from "react";
import dynamic from "next/dynamic";
import { CSSReset, ThemeProvider } from "@chakra-ui/core";
import _useMedia, { MediaProvider } from "~/components/MediaProvider";
import {
  StateProvider,
  useHyperglassState as _useHyperglassState
} from "~/components/StateProvider";
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
  // console.log(value);
  // console.log(theme);
  return (
    <HyperglassContext.Provider value={value}>
      <ThemeProvider theme={theme}>
        <ColorModeProvider value={config.web.theme.default_color_mode ?? null}>
          <CSSReset />
          <MediaProvider theme={theme}>
            <StateProvider>{children}</StateProvider>
          </MediaProvider>
        </ColorModeProvider>
      </ThemeProvider>
    </HyperglassContext.Provider>
  );
};

export default () => useContext(HyperglassContext);

export const useHyperglassState = _useHyperglassState;

export const useMedia = _useMedia;
