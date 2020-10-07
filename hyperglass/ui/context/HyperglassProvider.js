import * as React from 'react';
import { createContext, useContext, useMemo } from 'react';
import dynamic from 'next/dynamic';
import { CSSReset, ThemeProvider } from '@chakra-ui/core';
import { MediaProvider } from './MediaProvider';
import { StateProvider } from './StateProvider';
import { makeTheme, defaultTheme } from 'app/util';

// Disable SSR for ColorModeProvider
const ColorModeProvider = dynamic(
  () => import('@chakra-ui/core').then(mod => mod.ColorModeProvider),
  { ssr: false },
);

const HyperglassContext = createContext(null);

export const HyperglassProvider = ({ config, children }) => {
  const value = useMemo(() => config, [config]);
  const userTheme = value && makeTheme(value.web.theme);
  const theme = value ? userTheme : defaultTheme;
  return (
    <ThemeProvider theme={theme}>
      <ColorModeProvider value={config.web.theme.default_color_mode ?? null}>
        <CSSReset />
        <MediaProvider theme={theme}>
          <HyperglassContext.Provider value={value}>
            <StateProvider>{children}</StateProvider>
          </HyperglassContext.Provider>
        </MediaProvider>
      </ColorModeProvider>
    </ThemeProvider>
  );
};

export const useConfig = () => useContext(HyperglassContext);
