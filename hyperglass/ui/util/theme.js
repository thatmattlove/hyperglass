import { theme as chakraTheme } from '@chakra-ui/core';
import chroma from 'chroma-js';

const alphaColors = color => ({
  900: chroma(color)
    .alpha(0.92)
    .css(),
  800: chroma(color)
    .alpha(0.8)
    .css(),
  700: chroma(color)
    .alpha(0.6)
    .css(),
  600: chroma(color)
    .alpha(0.48)
    .css(),
  500: chroma(color)
    .alpha(0.38)
    .css(),
  400: chroma(color)
    .alpha(0.24)
    .css(),
  300: chroma(color)
    .alpha(0.16)
    .css(),
  200: chroma(color)
    .alpha(0.12)
    .css(),
  100: chroma(color)
    .alpha(0.08)
    .css(),
  50: chroma(color)
    .alpha(0.04)
    .css(),
});

const generateColors = colorInput => {
  const colorMap = {};

  const lightnessMap = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05];
  const saturationMap = [0.32, 0.16, 0.08, 0.04, 0, 0, 0.04, 0.08, 0.16, 0.32];

  const validColor = chroma.valid(colorInput.trim()) ? chroma(colorInput.trim()) : chroma('#000');

  const lightnessGoal = validColor.get('hsl.l');
  const closestLightness = lightnessMap.reduce((prev, curr) =>
    Math.abs(curr - lightnessGoal) < Math.abs(prev - lightnessGoal) ? curr : prev,
  );

  const baseColorIndex = lightnessMap.findIndex(l => l === closestLightness);

  const colors = lightnessMap
    .map(l => validColor.set('hsl.l', l))
    .map(color => chroma(color))
    .map((color, i) => {
      const saturationDelta = saturationMap[i] - saturationMap[baseColorIndex];
      return saturationDelta >= 0
        ? color.saturate(saturationDelta)
        : color.desaturate(saturationDelta * -1);
    });

  const getColorNumber = index => (index === 0 ? 50 : index * 100);

  colors.map((color, i) => {
    const colorIndex = getColorNumber(i);
    colorMap[colorIndex] = color.hex();
  });
  return colorMap;
};

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

const generatePalette = palette => {
  const generatedPalette = {};
  Object.keys(palette).map(color => {
    if (!['black', 'white'].includes(color)) {
      generatedPalette[color] = generateColors(palette[color]);
    } else {
      generatedPalette[color] = palette[color];
      generatedPalette[`${color}Alpha`] = alphaColors(palette[color]);
      generatedPalette[`${color}Faded`] = generateColors(palette[color]);
    }
  });
  return generatedPalette;
};

const formatFont = font => {
  const fontList = font.split(' ');
  const fontFmt = fontList.length >= 2 ? `'${fontList.join(' ')}'` : fontList.join(' ');
  return fontFmt;
};

const importFonts = userFonts => {
  const [body, mono] = [defaultBodyFonts, defaultMonoFonts];
  const bodyFmt = formatFont(userFonts.body);
  const monoFmt = formatFont(userFonts.mono);
  if (userFonts.body && !body.includes(bodyFmt)) {
    body.unshift(bodyFmt);
  }
  if (userFonts.mono && !mono.includes(monoFmt)) {
    mono.unshift(monoFmt);
  }
  return {
    body: body.join(', '),
    heading: body.join(', '),
    mono: mono.join(', '),
  };
};

const importColors = (userColors = {}) => {
  const generatedColors = generatePalette(userColors);
  return {
    transparent: 'transparent',
    current: 'currentColor',
    ...generatedColors,
  };
};

export const makeTheme = userTheme => ({
  ...chakraTheme,
  colors: importColors(userTheme.colors),
  fonts: importFonts(userTheme.fonts),
});

export const isDark = color => {
  // YIQ equation from http://24ways.org/2010/calculating-color-contrast
  const rgb = chroma(color).rgb();
  const yiq = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
  return yiq < 128;
};

export const isLight = color => isDark(color);

export const opposingColor = (theme, color) => {
  if (color.match(/^\w+\.\d+$/m)) {
    const colorParts = color.split('.');
    if (colorParts.length !== 2) {
      throw Error(`Color is improperly formatted. Got '${color}'`);
    }
    const [colorName, colorOpacity] = colorParts;
    color = theme.colors[colorName][colorOpacity];
  }
  const opposing = isDark(color) ? theme.colors.white : theme.colors.black;
  return opposing;
};

export const googleFontUrl = (fontFamily, weights = [300, 400, 700]) => {
  const urlWeights = weights.join(',');
  const fontName = fontFamily
    .split(/, /)[0]
    .trim()
    .replace(/'|"/g, '');
  const urlFont = fontName.split(/ /).join('+');
  const urlBase = `https://fonts.googleapis.com/css?family=${urlFont}:${urlWeights}&display=swap`;
  return urlBase;
};

export { theme as defaultTheme } from '@chakra-ui/core';
