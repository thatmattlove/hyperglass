import { theme as chakraTheme } from "@chakra-ui/core";
import chroma from "chroma-js";

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
        .css()
});

const generateColors = colorInput => {
    const colorMap = {};

    const lightnessMap = [0.95, 0.85, 0.75, 0.65, 0.55, 0.45, 0.35, 0.25, 0.15, 0.05];
    const saturationMap = [0.32, 0.16, 0.08, 0.04, 0, 0, 0.04, 0.08, 0.16, 0.32];

    const validColor = chroma.valid(colorInput.trim()) ? chroma(colorInput.trim()) : chroma("#000");

    const lightnessGoal = validColor.get("hsl.l");
    const closestLightness = lightnessMap.reduce((prev, curr) =>
        Math.abs(curr - lightnessGoal) < Math.abs(prev - lightnessGoal) ? curr : prev
    );

    const baseColorIndex = lightnessMap.findIndex(l => l === closestLightness);

    const colors = lightnessMap
        .map(l => validColor.set("hsl.l", l))
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

// const defaultBasePalette = {
//     black: "#262626",
//     white: "#f7f7f7",
//     gray: "#c1c7cc",
//     red: "#d84b4b",
//     orange: "ff6b35",
//     yellow: "#edae49",
//     green: "#35b246",
//     blue: "#314cb6",
//     teal: "#35b299",
//     cyan: "#118ab2",
//     pink: "#f2607d",
//     purple: "#8d30b5"
// };

// const defaultSwatchPalette = {
//     black: defaultBasePalette.black,
//     white: defaultBasePalette.white,
//     gray: generateColors(defaultBasePalette.gray),
//     red: generateColors(defaultBasePalette.red),
//     orange: generateColors(defaultBasePalette.orange),
//     yellow: generateColors(defaultBasePalette.yellow),
//     green: generateColors(defaultBasePalette.green),
//     blue: generateColors(defaultBasePalette.blue),
//     teal: generateColors(defaultBasePalette.teal),
//     cyan: generateColors(defaultBasePalette.cyan),
//     pink: generateColors(defaultBasePalette.pink),
//     purple: generateColors(defaultBasePalette.purple)
// };

// const defaultAlphaPalette = {
//     blackAlpha: alphaColors(defaultBasePalette.black),
//     whiteAlpha: alphaColors(defaultBasePalette.white)
// };

// const defaultFuncSwatchPalette = {
//     primary: generateColors(defaultBasePalette.cyan),
//     secondary: generateColors(defaultBasePalette.blue),
//     dark: generateColors(defaultBasePalette.black),
//     light: generateColors(defaultBasePalette.white),
//     success: generateColors(defaultBasePalette.green),
//     warning: generateColors(defaultBasePalette.yellow),
//     error: generateColors(defaultBasePalette.orange),
//     danger: generateColors(defaultBasePalette.red)
// };

// const defaultColors = {
//     transparent: "transparent",
//     current: "currentColor",
//     ...defaultFuncSwatchPalette,
//     ...defaultAlphaPalette,
//     ...defaultSwatchPalette
// };

const defaultBodyFonts = [
    // "Nunito",
    "-apple-system",
    "BlinkMacSystemFont",
    '"Segoe UI"',
    "Helvetica",
    "Arial",
    "sans-serif",
    '"Apple Color Emoji"',
    '"Segoe UI Emoji"',
    '"Segoe UI Symbol"'
];

const defaultMonoFonts = [
    // '"Fira Code"',
    "SFMono-Regular",
    "Melno",
    "Monaco",
    "Consolas",
    '"Liberation Mono"',
    '"Courier New"',
    "monospace"
];

// const defaultFonts = {
//     body: defaultBodyFonts.join(", "),
//     heading: defaultBodyFonts.join(", "),
//     mono: defaultMonoFonts.join(", ")
// };

// const defaultTheme = {
//     ...chakraTheme,
//     colors: defaultColors,
//     fonts: defaultFonts
// };

const generatePalette = palette => {
    const generatedPalette = {};
    Object.keys(palette).map(color => {
        if (!["black", "white"].includes(color)) {
            generatedPalette[color] = generateColors(palette[color]);
        } else {
            generatedPalette[color] = palette[color];
            generatedPalette[`${color}Alpha`] = alphaColors(palette[color]);
        }
    });
    return generatedPalette;
};

// const generateFuncPalette = palette => ({
//     primary: generateColors(palette.cyan),
//     secondary: generateColors(palette.blue),
//     dark: generateColors(palette.black),
//     light: generateColors(palette.white),
//     success: generateColors(palette.green),
//     warning: generateColors(palette.yellow),
//     error: generateColors(palette.orange),
//     danger: generateColors(palette.red)
// });

// const generateAlphaPalette = palette => ({
//     blackAlpha: alphaColors(palette.black),
//     whiteAlpha: alphaColors(palette.white)
// });

const formatFont = font => {
    const fontList = font.split(" ");
    const fontFmt = fontList.length >= 2 ? `'${fontList.join(" ")}'` : fontList.join(" ");
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
        body: body.join(", "),
        heading: body.join(", "),
        mono: mono.join(", ")
    };
};

const importColors = (userColors = {}) => {
    // const baseColors = {
    //     ...defaultBasePalette,
    //     ...userColors
    // };

    const generatedColors = generatePalette(userColors);
    // const swatchColors = generatePalette(baseColors);
    // const funcColors = generateFuncPalette(baseColors);
    // const bwAlphaColors = generateAlphaPalette(userColors);
    return {
        transparent: "transparent",
        current: "currentColor",
        // ...swatchColors,
        // ...funcColors,
        ...generatedColors
        // ...bwAlphaColors
    };
};

const makeTheme = userTheme => ({
    ...chakraTheme,
    colors: importColors(userTheme.colors),
    fonts: importFonts(userTheme.fonts)
});

export { makeTheme, chakraTheme as defaultTheme };
