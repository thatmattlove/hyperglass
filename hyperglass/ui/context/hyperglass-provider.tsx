import { createContext, useContext, useMemo } from 'react';
import { ChakraProvider } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { makeTheme, defaultTheme } from '~/util';

import type { Config } from '~/types';

interface HyperglassProviderProps {
  config: Config;
  children: React.ReactNode;
}

export const HyperglassContext = createContext<Config>({} as Config);

const queryClient = new QueryClient();

export const HyperglassProvider = (props: HyperglassProviderProps): JSX.Element => {
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
