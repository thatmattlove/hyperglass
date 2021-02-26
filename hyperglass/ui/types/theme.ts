import type { ChakraTheme } from '@chakra-ui/theme';

export namespace Theme {
  export type Colors = ChakraTheme['colors'];

  export type ColorNames = keyof Colors;

  export type Fonts = {
    body: string;
    mono: string;
  };

  export type FontWeights = Partial<ChakraTheme['fontWeights']>;

  export interface Full extends Omit<ChakraTheme, 'colors'> {
    colors: Colors;
  }
}
