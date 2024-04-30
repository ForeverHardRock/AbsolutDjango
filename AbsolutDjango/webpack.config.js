const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
    entry: '/Surveys/static/Surveys/js/app.js',
    mode: "development",
    output: {
        filename: 'bundle.js',
        path: __dirname + '/Surveys/static/dist/',
    },
    module: {
        rules: [
            {
                test: /\.s[ac]ss$/i,
                use: [
                    MiniCssExtractPlugin.loader,
                    'css-loader',
                    'sass-loader',
                ],
            },
        ],
    },
    plugins: [
        new MiniCssExtractPlugin({
            filename: 'style.css',
        }),
    ],
}