const aliases = require("./.alias");
const envVars = require("/tmp/hyperglass.env.json");
const { configFile } = envVars;
const config = require(String(configFile));
const generateFavicons = require("./generateFavicons");

const faviconHtmlFile = generateFavicons(
  config._HYPERGLASS_CONFIG_,
  config._HYPERGLASS_APP_PATH_
);

module.exports = {
  webpack(config) {
    const { alias } = config.resolve;
    config.resolve.alias = {
      ...alias,
      ...aliases
    };
    return config;
  },
  poweredByHeader: false,
  env: {
    _NODE_ENV_: config.NODE_ENV,
    _HYPERGLASS_URL_: config._HYPERGLASS_URL_,
    _HYPERGLASS_CONFIG_: config._HYPERGLASS_CONFIG_,
    _FAVICON_HTML_FILE_: faviconHtmlFile
  }
};
