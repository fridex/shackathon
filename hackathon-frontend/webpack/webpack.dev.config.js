var webpack = require('webpack');
var path = require('path');

var parentDir = path.join(__dirname, '../');

module.exports = {
  entry: [
    path.join(parentDir, 'index.js')
  ],
  module: {
    rules: [{
      test: /.(ts|tsx)$/,
      loader: 'awesome-typescript-loader'
    },{
      test: /\.(js|jsx)$/,
      exclude: /node_modules/,
      loader: 'babel-loader'
    },{
      test: /\.less$/,
      loaders: ['style-loader', 'css-loader', 'less-loader']
    }
    ]
  },
  resolve: {
    modules: ['pes', 'node_modules'],
    extensions: ['.js', '.jsx']
  },
  plugins: [
    new webpack.ProvidePlugin({
      $: 'jquery',
      jQuery: 'jquery'
    }),
  ],
  output: {
    path: parentDir + '/assets',
    filename: 'bundle.js',
    publicPath: 'assets/',
  },
  devServer: {
    contentBase: parentDir,
    historyApiFallback: true,
    host: '0.0.0.0',
    port: 1337,
    inline: true,
    hot: true,
    proxy: {
      '/api': 'http://localhost:8000/'
    }
  },
  externals: {
    'cheerio': 'window',
    'react/lib/ExecutionEnvironment': true,
    'react/lib/ReactContext': true,
  },
  mode: 'development',
  devtool: 'source-map'
};
