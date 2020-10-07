/* eslint-disable no-console */
const express = require('express');
const proxyMiddleware = require('http-proxy-middleware');
const next = require('next');
const envVars = require('/tmp/hyperglass.env.json');
const { configFile } = envVars;
const config = require(String(configFile));

const { NODE_ENV: env, _HYPERGLASS_URL_: envUrl } = config;

const devProxy = {
  '/api/query/': { target: envUrl + 'api/query/', pathRewrite: { '^/api/query/': '' } },
  '/images': { target: envUrl + 'images', pathRewrite: { '^/images': '' } },
  '/custom': { target: envUrl + 'custom', pathRewrite: { '^/custom': '' } },
};

const port = parseInt(process.env.PORT, 10) || 3000;
const dev = env !== 'production';
const app = next({
  dir: '.', // base directory where everything is, could move to src later
  dev,
});

const handle = app.getRequestHandler();

let server;
app
  .prepare()
  .then(() => {
    server = express();

    // Set up the proxy.
    if (dev && devProxy) {
      Object.keys(devProxy).forEach(function(context) {
        server.use(proxyMiddleware(context, devProxy[context]));
      });
    }

    // Default catch-all handler to allow Next.js to handle all other routes
    server.all('*', (req, res) => handle(req, res));

    server.listen(port, err => {
      if (err) {
        throw err;
      }
      console.log(`> Ready on port ${port} [${env}]`);
    });
  })
  .catch(err => {
    console.log('An error occurred, unable to start the server');
    console.log(err);
  });
