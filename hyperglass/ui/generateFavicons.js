const fs = require("fs");
const favicons = require("favicons");
const tempy = require("tempy");

const defaultConfig = {
  path: "/images/favicons",
  appleStatusBarStyle: "black-translucent",
  display: "standalone",
  orientation: "any",
  scope: "/",
  icons: {
    android: true,
    appleIcon: true,
    appleStartup: true,
    coast: true,
    favicons: true,
    firefox: true,
    windows: true,
    yandex: true
  }
};

const handleError = err => {
  if (err) {
    if (err.message) {
      console.error(err.message);
      return;
    }
    console.error(err);
    return;
  }
  return;
};

const writeHtml = (path, data) => {
  fs.writeFile(path, data, handleError);
  return;
};

const writeFiles = (basePath, files) => {
  files.forEach(attrs => {
    fs.writeFile(`${basePath}/${attrs.name}`, attrs.contents, handleError);
  });
  return;
};

const generateFavicons = (config, appPath) => {
  const htmlFile = tempy.file({ extension: "json" });
  const callback = (err, response) => {
    handleError(err);
    writeFiles(`${appPath}/static/images/favicons`, response.images);
    writeFiles(`${appPath}/static/images/favicons`, response.files);
    writeHtml(htmlFile, JSON.stringify(response.html));
    return;
  };

  favicons(
    config.web.logo.favicon,
    {
      appName: config.site_title,
      appDescription: config.site_description,
      lang: config.language || "en-US",
      background: config.web.theme.colors.white,
      theme_color: config.web.theme.colors.primary,
      ...defaultConfig
    },
    callback
  );
  return htmlFile;
};

module.exports = generateFavicons;
