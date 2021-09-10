/* eslint-disable no-console */
const express = require('express');
const proxyMiddleware = require('http-proxy-middleware');
const next = require('next');
const config = require('/tmp/hyperglass.env.json');

const {
  env: { NODE_ENV },
  hyperglass: { url },
} = config;

const devProxy = {
  '/api/query/': { target: url + 'api/query/', pathRewrite: { '^/api/query/': '' } },
  '/ui/props/': { target: url + 'ui/props/', pathRewrite: { '^/ui/props/': '' } },
  '/images': { target: url + 'images', pathRewrite: { '^/images': '' } },
  '/custom': { target: url + 'custom', pathRewrite: { '^/custom': '' } },
};

const port = parseInt(process.env.PORT, 10) || 3000;
const dev = NODE_ENV !== 'production';
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
      Object.keys(devProxy).forEach(function (context) {
        server.use(proxyMiddleware(context, devProxy[context]));
      });
    }

    // Default catch-all handler to allow Next.js to handle all other routes
    server.all('*', (req, res) => handle(req, res));

    server.listen(port, err => {
      if (err) {
        throw err;
      }
      console.log(`> Ready on port ${port} [${NODE_ENV}]`);
    });
  })
  .catch(err => {
    console.log('An error occurred, unable to start the server');
    console.log(err);
  });
