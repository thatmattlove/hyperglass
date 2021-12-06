import { createContext, useContext, useMemo } from 'react';
import {
  useToken,
  ChakraProvider,
  useColorModeValue,
  useBreakpointValue,
  useTheme as useChakraTheme,
} from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { makeTheme, defaultTheme } from '~/util';

import type { Config, Theme } from '~/types';
import type { THyperglassProvider } from './types';

export const HyperglassContext = createContext<Config>({} as Config);

const queryClient = new QueryClient();

export const HyperglassProvider: React.FC<THyperglassProvider> = (props: THyperglassProvider) => {
  const { config, children } = props;
  const value = useMemo(() => config, [config]);
  const userTheme = value && makeTheme(value.web.theme, value.web.theme.defaultColorMode);
  const theme = value ? userTheme : defaultTheme;
  return (
    <ChakraProvider theme={theme}>
      <HyperglassContext.Provider value={value}>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </HyperglassContext.Provider>
    </ChakraProvider>
  );
};

/**
 * Get the current configuration.
 */
export const useConfig = (): Config => useContext(HyperglassContext);

/**
 * Get the current theme object.
 */
export const useTheme = (): Theme.Full => useChakraTheme();

/**
 * Determine if device is mobile or desktop based on Chakra UI theme breakpoints.
 */
export const useMobile = (): boolean =>
  useBreakpointValue<boolean>({ base: true, md: true, lg: false, xl: false }) ?? true;

/**
 * Convenience function to combine Chakra UI's useToken & useColorModeValue.
 */
export const useColorToken = <L extends string, D extends string>(
  token: keyof Theme.Full,
  light: L,
  dark: D,
): L | D => useColorModeValue(useToken(token, light), useToken(token, dark));

export {
  useColorMode,
  useBreakpointValue,
  useColorModeValue as useColorValue,
} from '@chakra-ui/react';
