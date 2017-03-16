var webpack = require('webpack');
var path = require('path');
var BundleTracker = require('webpack-bundle-tracker');

var BUILD_DIR = path.resolve(__dirname, 'src/client/public/');
var APP_DIR = path.resolve(__dirname, 'src/client/app/');

var config = {
  entry: APP_DIR + '/index.jsx',
  output: {
    path: BUILD_DIR,
    filename: 'bundle.js' // Creates a bundle.js file in the build dir
  },
  plugins: [
    new BundleTracker({filename: './webpack-stats.json'}),
  ],
  module : {
    loaders : [
      {
        test : /\.jsx?/, // This regex allows us to test both jsx and js
        include : APP_DIR,
        loader : 'babel-loader'
        // before you can use 'babel', now you have to use 'babel-loader'
      },
        {
        test: /\.css$/,
        loader: 'style-loader!css-loader'
      },
    ]
  },
};

module.exports = config;
