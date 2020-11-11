var path = require('path');
const getPreprocessor = require('svelte-preprocess');
const CopyPlugin = require('copy-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const postcssPlugins = require('./postcss.config.js');
const globby = require('globby');

const mode = process.env.NODE_ENV || 'development';
const isDevBuild = mode !== 'production';

const cssConfig = {
  test: /\.(sa|sc|c)ss$/,
  use: [
    MiniCssExtractPlugin.loader,
    'css-loader',
    { loader: 'postcss-loader', options: { extract: true, plugins: postcssPlugins(!isDevBuild) } },
  ],
};


function getEntries() {
  try {
    const entries = {};
    const allEntry = globby.sync('src/pages/**/main.js');
    allEntry.forEach(entry => {
      const res = entry.match(/src\/pages\/(\w+)\/main\.js/);
      if (res.length) {
        entries[res[1]] = `./${entry}`;
      }
    });
    return entries;
  } catch (error) {
    console.error('File structure maybe incorrect for MPA', error);
  }
}

function multiHtmlPlugin(entries) {
  const pageNames = Object.keys(entries);
  return pageNames.map(name => {
    return new HtmlWebpackPlugin({
      filename: `${name}.html`,
      template: './public/index.html',
      chunks: [name],
      minify: !isDevBuild
        ? {
            removeComments: true,
            collapseWhitespace: true,
            minifyCSS: true,
          }
        : true,
    });
  });
}


const preprocess = getPreprocessor({
  transformers: {
    postcss: {
      plugins: postcssPlugins()
    }
  }
});
const entry = getEntries();
const htmlPlugins = multiHtmlPlugin(entry);
module.exports = {
  entry,
    output: {
      path: path.join(__dirname, 'dist'),
      filename: 'public/js/[name].[hash].js',
      chunkFilename: 'public/js/[name].[chunkhash].js',
    },
  mode,
  module: {
    rules: [      
      cssConfig,
      {
        test: /\.svelte$/,
        use: { loader: 'svelte-loader', options: { 
            dev: isDevBuild, 
            preprocess,
          } 
        },
        exclude: ['/node_modules/']
      },     
      {
        test: /\.(png|jpe?g|gif|svg)$/,
        loader: 'file-loader',
        options: { name: 'public/img/[name].[hash:7].[ext]' }
      },
      {
          test: /\.(woff2?|eot|ttf|otf)(\?.*)?$/,
          loader: 'file-loader',
          options: {
            limit: 10000,
            name: 'public/fonts/[name].[hash:7].[ext]',
          },
        },
    ]
  },
  resolve: {
    extensions: ['.mjs', '.js', '.json', '.svelte'],
    mainFields: ['svelte', 'module', 'main'],
  },
  performance: {
    hints: false
  },

  plugins: [
    new MiniCssExtractPlugin({
        filename: 'public/css/[name].[contenthash].css',
      }),
    new CopyPlugin([{ from: './public/static', to: './public/static' }]),
      ...htmlPlugins,
  ]
}

if (!isDevBuild) {
  module.exports.optimization = {
    minimize: true,
  }
} else {
  module.exports.devtool = '#source-map';

  module.exports.devServer = {
    port: 9000,
    host: "localhost",
    historyApiFallback: true,
    watchOptions: {aggregateTimeout: 300, poll: 1000},
    contentBase: './public',
    open: true
  };
}