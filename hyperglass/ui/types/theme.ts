import type { Theme as DefaultTheme } from '@chakra-ui/theme';
import type { ColorHues } from '@chakra-ui/theme/dist/types/foundations/colors';

export namespace Theme {
  type ExtraColors = {
    primary: ColorHues;
    secondary: ColorHues;
    tertiary: ColorHues;
    dark: ColorHues;
    light: ColorHues;
    success: ColorHues;
    blackSolid: ColorHues;
    whiteSolid: ColorHues;
  };

  export type Colors = ExtraColors & DefaultTheme['colors'];

  export type ColorNames = keyof Colors;

  export type Fonts = {
    body: string;
    mono: string;
  };

  export type FontWeights = Partial<DefaultTheme['fontWeights']>;

  export interface Full extends Omit<DefaultTheme, 'colors'> {
    colors: Colors;
  }
}
