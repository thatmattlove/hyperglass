/* eslint-disable no-console */
const express = require('express');
const proxyMiddleware = require('http-proxy-middleware');
const next = require('next');

const port = parseInt(process.env.PORT, 10) || 3000;
const dev = process.env.NODE_ENV !== 'production';
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

    const devProxy = {
      '/api/query/': {
        target: `${process.env.HYPERGLASS_URL}api/query/`,
        pathRewrite: { '^/api/query/': '' },
      },
      '/ui/props/': {
        target: `${process.env.HYPERGLASS_URL}ui/props/`,
        pathRewrite: { '^/ui/props/': '' },
      },
      '/images': { target: `${process.env.HYPERGLASS_URL}images`, pathRewrite: { '^/images': '' } },
    };

    // Set up the proxy.
    if (dev) {
      // biome-ignore lint/complexity/noForEach: not messing with Next's example code.
      Object.keys(devProxy).forEach(context => {
        server.use(proxyMiddleware(context, devProxy[context]));
      });
    }

    // Default catch-all handler to allow Next.js to handle all other routes
    server.all('*', (req, res) => handle(req, res));

    server.listen(port, err => {
      if (err) {
        throw err;
      }
      console.log(`> Ready on port ${port} [${process.env.NODE_ENV}]`);
    });
  })
  .catch(err => {
    console.log('An error occurred, unable to start the server');
    console.log(err);
  });
