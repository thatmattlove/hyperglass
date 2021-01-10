import {
  hsla,
  saturate,
  desaturate,
  parseToHsla,
  transparentize,
  readableColorIsBlack,
} from 'color2k';
import { extendTheme } from '@chakra-ui/react';
import { mode } from '@chakra-ui/theme-tools';

import type { Theme as ChakraTheme } from '@chakra-ui/react';
import type { IConfigTheme, Theme } from '~/types';

const defaultBodyFonts = [
  '-apple-system',
  'BlinkMacSystemFont',
  '"Segoe UI"',
  'Helvetica',
  'Arial',
  'sans-serif',
  '"Apple Color Emoji"',
  '"Segoe UI Emoji"',
  '"Segoe UI Symbol"',
];

const defaultMonoFonts = [
  'SFMono-Regular',
  'Melno',
  'Monaco',
  'Consolas',
  '"Liberation Mono"',
  '"Courier New"',
  'monospace',
];

export function isLight(color: string): boolean {
  return readableColorIsBlack(color);
}

export function isDark(color: string): boolean {
  return !readableColorIsBlack(color);
}

function alphaColors(color: string) {
  return {
    50: transparentize(color, Number((1 - 0.04).toFixed(2))),
    100: transparentize(color, Number((1 - 0.08).toFixed(2))),
    200: transparentize(color, Number((1 - 0.12).toFixed(2))),
    300: transparentize(color, Number((1 - 0.16).toFixed(2))),
    400: transparentize(color, Number((1 - 0.24).toFixed(2))),
    500: transparentize(color, Number((1 - 0.38).toFixed(2))),
    600: transparentize(color, Number((1 - 0.48).toFixed(2))),
    700: transparentize(color, Number((1 - 0.6).toFixed(2))),
    800: transparentize(color, Number((1 - 0.8).toFixed(2))),
    900: transparentize(color, Number((1 - 0.92).toFixed(2))),
  };
}

function generateColors(colorInput: string) {
  const colorMap = Object();

  const lightnessMap = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05];
  const saturationMap = [0.32, 0.16, 0.08, 0.04, 0, 0, 0.04, 0.08, 0.16, 0.32];

  const colorHsla = parseToHsla(colorInput);
  const lightnessGoal = colorHsla[2];

  const closestLightness = lightnessMap.reduce((prev, curr) =>
    Math.abs(curr - lightnessGoal) < Math.abs(prev - lightnessGoal) ? curr : prev,
  );

  const baseColorIndex = lightnessMap.findIndex(l => l === closestLightness);

  const colors = lightnessMap
    .map(l => {
      const [h, s, _, a] = colorHsla;
      return hsla(h, s, l, a);
    })
    .map((color, i) => {
      const saturationDelta = saturationMap[i] - saturationMap[baseColorIndex];
      return saturationDelta >= 0
        ? saturate(color, saturationDelta)
        : desaturate(color, saturationDelta * -1);
    });

  const getColorNumber = (index: number) => (index === 0 ? 50 : index * 100);

  colors.map((color, i) => {
    const colorIndex = getColorNumber(i);
    if (colorIndex === 500) {
      colorMap[500] = colorInput;
    } else {
      colorMap[colorIndex] = color;
    }
  });
  return colorMap;
}

function generatePalette(palette: IConfigTheme['colors']): Theme.Colors {
  const generatedPalette = Object();

  for (const color of Object.keys(palette)) {
    if (!['black', 'white'].includes(color)) {
      generatedPalette[color] = generateColors(palette[color]);
    } else {
      generatedPalette[color] = palette[color];
      generatedPalette[`${color}Alpha`] = alphaColors(palette[color]);
    }
  }

  generatedPalette.blackSolid = {
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
  };
  generatedPalette.whiteSolid = {
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
  };
  return generatedPalette;
}

function formatFont(font: string): string {
  const fontList = font.split(' ');
  const fontFmt = fontList.length >= 2 ? `'${fontList.join(' ')}'` : fontList.join(' ');
  return fontFmt;
}

function importFonts(userFonts: Theme.Fonts): [ChakraTheme['fonts'], Theme.FontWeights] {
  const [body, mono] = [defaultBodyFonts, defaultMonoFonts];
  const { body: userBody, mono: userMono, ...fontWeights } = userFonts;
  const bodyFmt = formatFont(userBody);
  const monoFmt = formatFont(userMono);
  if (userFonts.body && !body.includes(bodyFmt)) {
    body.unshift(bodyFmt);
  }
  if (userFonts.mono && !mono.includes(monoFmt)) {
    mono.unshift(monoFmt);
  }
  return [
    {
      body: body.join(', '),
      heading: body.join(', '),
      mono: mono.join(', '),
    },
    fontWeights,
  ];
}

function importColors(userColors: IConfigTheme['colors']): Theme.Colors {
  const generatedColors = generatePalette(userColors);

  return {
    ...generatedColors,
    transparent: 'transparent',
    current: 'currentColor',
  };
}

export function makeTheme(
  userTheme: IConfigTheme,
  defaultColorMode: 'dark' | 'light' | null,
): Theme.Full {
  const [fonts, fontWeights] = importFonts(userTheme.fonts);
  const colors = importColors(userTheme.colors);
  const config = {} as Theme.Full['config'];

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

  const defaultTheme = extendTheme({
    fonts,
    colors,
    config,
    fontWeights,
    styles: {
      global: props => ({
        html: { scrollBehavior: 'smooth', height: '-webkit-fill-available' },
        body: {
          background: mode('light.500', 'dark.500')(props),
          color: mode('black', 'white')(props),
        },
      }),
    },
  });

  return defaultTheme;
}

export function googleFontUrl(fontFamily: string, weights: number[] = [300, 400, 700]): string {
  const urlWeights = weights.join(',');
  const fontName = fontFamily.split(/, /)[0].trim().replace(/'|"/g, '');
  const urlFont = fontName.split(/ /).join('+');
  return `https://fonts.googleapis.com/css?family=${urlFont}:${urlWeights}&display=swap`;
}

export { theme as defaultTheme } from '@chakra-ui/react';
