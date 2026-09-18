const path = require('path');
const { DefinePlugin } = require('webpack');
const { VueLoaderPlugin } = require('vue-loader');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

require('dotenv').config();

module.exports = (env, argv) => {
  const isProd = argv.mode === 'production';

  return {
    entry: './src/main.js',
    output: {
      path: path.resolve(__dirname, 'dist'),
      filename: isProd ? 'js/[name].[contenthash].js' : 'js/[name].js',
      publicPath: '/',
      clean: true,
    },
    resolve: {
      extensions: ['.js', '.vue'],
      alias: { '@': path.resolve(__dirname, 'src') },
    },
    module: {
      rules: [
        { test: /\.vue$/, loader: 'vue-loader' },
        {
          test: /\.s?css$/,
          use: [
            isProd ? MiniCssExtractPlugin.loader : 'style-loader',
            'css-loader',
            {
              loader: 'sass-loader',
              options: {
                sassOptions: {
                  quietDeps: true,
                  silenceDeprecations: ['import'],
                },
              },
            },
          ],
        },
      ],
    },
    plugins: [
      new VueLoaderPlugin(),
      new HtmlWebpackPlugin({ template: './public/index.html', title: 'Transway' }),
      new DefinePlugin({
        __VUE_OPTIONS_API__: 'false',
        __VUE_PROD_DEVTOOLS__: 'false',
        __VUE_PROD_HYDRATION_MISMATCH_DETAILS__: 'false',
        'process.env.API_BASE_URL': JSON.stringify(process.env.API_BASE_URL || 'http://localhost:8000'),
        'process.env.GOOGLE_MAPS_API_KEY': JSON.stringify(process.env.GOOGLE_MAPS_API_KEY || ''),
        'process.env.GOOGLE_MAPS_MAP_ID': JSON.stringify(process.env.GOOGLE_MAPS_MAP_ID || ''),
      }),
      ...(isProd ? [new MiniCssExtractPlugin({ filename: 'css/[name].[contenthash].css' })] : []),
    ],
    devServer: {
      port: 8080,
      hot: true,
      historyApiFallback: true,
    },
    performance: {
      maxEntrypointSize: 512000,
      maxAssetSize: 512000,
    },
    devtool: isProd ? false : 'eval-source-map',
  };
};
