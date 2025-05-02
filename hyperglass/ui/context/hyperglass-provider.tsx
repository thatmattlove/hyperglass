import { ChakraProvider, localStorageManager } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { createContext, useContext, useMemo } from 'react';
import { makeTheme } from '~/util';

import type { Config } from '~/types';

interface HyperglassProviderProps {
  config: Config;
  children: React.ReactNode;
}

export const HyperglassContext = createContext<Config>({} as Config);

export const queryClient = new QueryClient();

export const HyperglassProvider = (props: HyperglassProviderProps): JSX.Element => {
  const { config, children } = props;
  const value = useMemo(() => config, []); // eslint-disable-line react-hooks/exhaustive-deps
  const theme = useMemo(() => makeTheme(value.web.theme, value.web.theme.defaultColorMode), []); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <HyperglassContext.Provider value={value}>
      <ChakraProvider theme={theme} colorModeManager={localStorageManager} resetCSS>
        <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
      </ChakraProvider>
    </HyperglassContext.Provider>
  );
};

/**
 * Get the current configuration.
 */
export const useConfig = (): Config => useContext(HyperglassContext);
