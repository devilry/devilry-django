const path = require('path');
const webpack = require('webpack');
const appconfig = require("./ievv_buildstatic.appconfig.json");

const import_paths = [path.resolve(__dirname, 'node_modules')];
Array.prototype.push.apply(import_paths, appconfig.npmrun_jsbuild.import_paths);

const include = appconfig.npmrun_jsbuild.import_paths.slice();
include.push(path.resolve(__dirname, "scripts/javascript"));

const webpackConfig = {
    entry: path.resolve(__dirname, 'scripts/javascript/devilry_all.js'),
    output: {
        filename: 'devilry_all.js',
        path: path.resolve(appconfig.destinationfolder, 'scripts'),
        target: 'web'
    },
    resolve: {
        root: import_paths,
        extensions: [".js", ""]
    },
    resolveLoader: {
        // We only want loaders to be resolved from node_modules
        // in this directory (not in any of the other packages, and
        // not from other directories).
        root: path.resolve(__dirname, 'node_modules')
    },
    module: {
        loaders: [
            {
                test: /.js$/,
                loader: 'babel-loader',
                exclude: /node_modules/,
                include: include,
                query: {
                    presets: [
                        'babel-preset-es2015'
                    ].map(require.resolve)
                }
            },
            {
                test: /.json$/,
                loader: 'json-loader'
            }
        ]
    },
    plugins: []
};

if(appconfig.is_in_production_mode) {
    webpackConfig.devtool = 'source-map';
    webpackConfig.plugins.push(
        new webpack.DefinePlugin({
            'process.env': {
                'NODE_ENV': JSON.stringify('production')
            }
        })
    );
} else {
    webpackConfig.devtool = 'cheap-module-eval-source-map';
    webpackConfig.output.pathinfo = true;
}


module.exports = webpackConfig;
