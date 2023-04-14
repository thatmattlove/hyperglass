import { createContext, useContext, useMemo } from 'react';
import { ChakraProvider, localStorageManager } from '@chakra-ui/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { makeTheme } from '~/util';

import type { Config } from '~/types';

interface HyperglassProviderProps {
  config: Config;
  children: React.ReactNode;
}

export const HyperglassContext = createContext<Config>({} as Config);

const queryClient = new QueryClient();

export const HyperglassProvider = (props: HyperglassProviderProps): JSX.Element => {
  const { config, children } = props;
  const value = useMemo(() => config, []);
  const theme = useMemo(() => makeTheme(value.web.theme, value.web.theme.defaultColorMode), []);

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
