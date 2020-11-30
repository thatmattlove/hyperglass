import { createContext, useContext, useMemo } from 'react';
import {
  useToken,
  ChakraProvider,
  useColorModeValue,
  useBreakpointValue,
  useTheme as useChakraTheme,
} from '@chakra-ui/react';
import { makeTheme, defaultTheme } from '~/util';

import type { IConfig, ITheme } from '~/types';
import type { THyperglassProvider } from './types';

const HyperglassContext = createContext<IConfig>(Object());

export const HyperglassProvider = (props: THyperglassProvider) => {
  const { config, children } = props;
  const value = useMemo(() => config, []);
  const userTheme = value && makeTheme(value.web.theme);
  const theme = value ? userTheme : defaultTheme;
  return (
    <ChakraProvider theme={theme}>
      <HyperglassContext.Provider value={value}>{children}</HyperglassContext.Provider>
    </ChakraProvider>
  );
};

export const useConfig = (): IConfig => useContext(HyperglassContext);
export const useTheme = (): ITheme => useChakraTheme();

export const useMobile = (): boolean =>
  useBreakpointValue({ base: true, md: true, lg: false, xl: false }) ?? true;

export const useColorToken = (light: string, dark: string): ValueOf<ITheme['colors']> =>
  useColorModeValue(useToken('colors', light), useToken('colors', dark));

export {
  useColorMode,
  useBreakpointValue,
  useColorModeValue as useColorValue,
} from '@chakra-ui/react';
