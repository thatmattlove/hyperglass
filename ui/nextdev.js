/* eslint-disable no-console */
const express = require("express");
const next = require("next");
const envVars = require("/tmp/hyperglass.env.json");
const env = envVars.NODE_ENV;
const envUrl = envVars._HYPERGLASS_URL_;

const devProxy = {
    "/api/config": { target: envUrl + "config", pathRewrite: { "^/api/config": "" } },
    "/api/query": { target: envUrl + "query", pathRewrite: { "^/api/query": "" } },
    "/images": { target: envUrl + "images", pathRewrite: { "^/images": "" } }
};

const port = parseInt(process.env.PORT, 10) || 3000;
const dev = env !== "production";
const app = next({
    dir: ".", // base directory where everything is, could move to src later
    dev
});

const handle = app.getRequestHandler();

let server;
app.prepare()
    .then(() => {
        server = express();

        // Set up the proxy.
        if (dev && devProxy) {
            const proxyMiddleware = require("http-proxy-middleware");
            Object.keys(devProxy).forEach(function(context) {
                server.use(proxyMiddleware(context, devProxy[context]));
            });
        }

        // Default catch-all handler to allow Next.js to handle all other routes
        server.all("*", (req, res) => handle(req, res));

        server.listen(port, err => {
            if (err) {
                throw err;
            }
            console.log(`> Ready on port ${port} [${env}]`);
        });
    })
    .catch(err => {
        console.log("An error occurred, unable to start the server");
        console.log(err);
    });
