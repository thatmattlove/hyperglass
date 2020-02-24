import chroma from "chroma-js";

const isDark = color => {
    // YIQ equation from http://24ways.org/2010/calculating-color-contrast
    const rgb = chroma(color).rgb();
    const yiq = (rgb[0] * 299 + rgb[1] * 587 + rgb[2] * 114) / 1000;
    return yiq < 128;
};

const isLight = color => isDark(color);

const opposingColor = (theme, color) => {
    const opposing = isDark(color) ? theme.colors.white : theme.colors.black;
    return opposing;
};

const googleFontUrl = (fontFamily, weights = [300, 400, 700]) => {
    const urlWeights = weights.join(",");
    const fontName = fontFamily
        .split(/, /)[0]
        .trim()
        .replace(/'|"/g, "");
    const urlFont = fontName.split(/ /).join("+");
    const urlBase = `https://fonts.googleapis.com/css?family=${urlFont}:${urlWeights}&display=swap`;
    return urlBase;
};

export { isDark, isLight, opposingColor, googleFontUrl };
