import * as React from 'react';
import { createContext, useContext, useMemo } from 'react';
import { ChakraProvider, useColorModeValue } from '@chakra-ui/core';
import { makeTheme, defaultTheme } from '~/util';

import type { IConfig } from '~/types';
import type { IHyperglassProvider } from './types';

const HyperglassContext = createContext<IConfig>(Object());

export const HyperglassProvider = (props: IHyperglassProvider) => {
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

export const useConfig = () => useContext(HyperglassContext);
export const useColorValue = useColorModeValue;
