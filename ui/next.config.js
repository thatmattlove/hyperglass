const aliases = require("./.alias");

module.exports = {
    webpack(config) {
        const { alias } = config.resolve;
        config.resolve.alias = {
            ...alias,
            ...aliases
        };
        return config;
    },
    poweredByHeader: false
};
