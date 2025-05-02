interface Favicon {
    rel: string | null;
    dimensions: [number, number];
    image_format: string;
    prefix: string;
}

export default [
    { dimensions: [48, 48], image_format: "ico", prefix: "favicon", rel: null },
    { dimensions: [16, 16], image_format: "png", prefix: "favicon", rel: "icon" },
    { dimensions: [32, 32], image_format: "png", prefix: "favicon", rel: "icon" },
    { dimensions: [64, 64], image_format: "png", prefix: "favicon", rel: "icon" },
    { dimensions: [96, 96], image_format: "png", prefix: "favicon", rel: "icon" },
    { dimensions: [180, 180], image_format: "png", prefix: "favicon", rel: "icon" },
    {
        dimensions: [57, 57],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [60, 60],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [72, 72],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [76, 76],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [114, 114],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [120, 120],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [144, 144],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [152, 152],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [167, 167],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    {
        dimensions: [180, 180],
        image_format: "png",
        prefix: "apple-touch-icon",
        rel: "apple-touch-icon",
    },
    { dimensions: [70, 70], image_format: "png", prefix: "mstile", rel: null },
    { dimensions: [270, 270], image_format: "png", prefix: "mstile", rel: null },
    { dimensions: [310, 310], image_format: "png", prefix: "mstile", rel: null },
    { dimensions: [310, 150], image_format: "png", prefix: "mstile", rel: null },
    { dimensions: [196, 196], image_format: "png", prefix: "favicon", rel: "shortcut icon" },
] as Favicon[];
