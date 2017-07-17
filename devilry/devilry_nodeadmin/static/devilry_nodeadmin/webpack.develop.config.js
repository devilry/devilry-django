const path = require('path');
const webpack = require('webpack');

const webpackConfig = {
  entry: path.resolve(__dirname, 'app/entry.js'),
  output: {
    filename: 'debug.js',
    path: __dirname,
    target: 'web',
    pathinfo: true
  },
  resolve: {
    root: [path.resolve(__dirname, 'node_modules')],
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
        test: /.json$/,
        loader: 'json-loader'
      }
    ]
  },
  plugins: [],
  devtool: 'cheap-module-eval-source-map'
};

module.exports = webpackConfig;
