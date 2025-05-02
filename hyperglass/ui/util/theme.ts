import { extendTheme } from '@chakra-ui/react';
import { generateFontFamily, generatePalette } from 'palette-by-numbers';

import type { ChakraTheme } from '@chakra-ui/react';
import type { ThemeConfig, Theme } from '~/types';

function importFonts(userFonts: Theme.Fonts): ChakraTheme['fonts'] {
  const { body: userBody, mono: userMono } = userFonts;

  return {
    body: generateFontFamily('sans-serif', userBody),
    heading: generateFontFamily('sans-serif', userBody),
    mono: generateFontFamily('monospace', userMono),
  };
}

function importColors(userColors: ThemeConfig['colors']): Theme.Colors {
  const initial: Pick<Theme.Colors, 'blackSolid' | 'whiteSolid' | 'transparent' | 'current'> = {
    blackSolid: {
      50: '#444444',
      100: '#3c3c3c',
      200: '#353535',
      300: '#2d2d2d',
      400: '#262626',
      500: '#1e1e1e',
      600: '#171717',
      700: '#0f0f0f',
      800: '#080808',
      900: '#000000',
    },
    whiteSolid: {
      50: '#ffffff',
      100: '#f7f7f7',
      200: '#f0f0f0',
      300: '#e8e8e8',
      400: '#e1e1e1',
      500: '#d9d9d9',
      600: '#d2d2d2',
      700: '#cacaca',
      800: '#c3c3c3',
      900: '#bbbbbb',
    },
    transparent: 'transparent',
    current: 'currentColor',
  };

  const generatedColors = Object.entries<string>(userColors).reduce<Theme.Colors>(
    (final, [k, v]) => {
      final[k] = generatePalette(v);
      return final;
    },
    initial,
  );

  return generatedColors;
}

export function makeTheme(
  userTheme: ThemeConfig,
  defaultColorMode: 'dark' | 'light' | null,
): Theme.Full {
  const fonts = importFonts(userTheme.fonts);
  const { white, black, ...otherColors } = userTheme.colors;
  const colors = importColors(otherColors);
  const config = {} as Theme.Full['config'];
  const fontWeights = {
    hairline: 300,
    thin: 300,
    light: 300,
    normal: 400,
    medium: 400,
    semibold: 700,
    bold: 700,
    extrabold: 700,
    black: 700,
  } as ChakraTheme['fontWeights'];

  switch (defaultColorMode) {
    case null:
      config.useSystemColorMode = true;
      break;
    case 'light':
      config.initialColorMode = 'light';
      break;
    case 'dark':
      config.initialColorMode = 'dark';
      break;
  }

  return extendTheme({
    fonts,
    colors,
    config,
    fontWeights,
    semanticTokens: {
      colors: {
        'body-bg': {
          default: 'light.500',
          _dark: 'dark.500',
        },
        'body-fg': {
          default: 'dark.500',
          _dark: 'light.500',
        },
      },
    },
    styles: {
      global: {
        html: { scrollBehavior: 'smooth', height: '-webkit-fill-available' },
        body: {
          background: 'body-bg',
          color: 'body-fg',
          overflowX: 'hidden',
        },
      },
    },
  }) as Theme.Full;
}

export function googleFontUrl(fontFamily: string, weights: number[] = [300, 400, 700]): string {
  const urlWeights = weights.join(',');
  const fontName = fontFamily.split(/, /)[0].trim().replace(/'|"/g, '');
  const urlFont = fontName.split(/ /).join('+');
  return `https://fonts.googleapis.com/css?family=${urlFont}:${urlWeights}&display=swap`;
}
