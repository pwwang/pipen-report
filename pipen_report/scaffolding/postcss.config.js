const extractor = require("smelte/src/utils/css-extractor.js");

const defaultWhitelist = ["html", "body", "stroke-primary", "mode-dark"];

const defaultWhitelistPatterns = [
  // for JS ripple
  /ripple/,
  // date picker
  /w\-.\/7/
];

module.exports = (purge = false) => {
  const tailwind = {},
    postcss = [],
    whitelist = defaultWhitelist,
    whitelistPatterns = defaultWhitelistPatterns;
  const tailwindConfig = require("./tailwind.config.js")(tailwind);
  return [
    require("postcss-import")(),
    require("postcss-url")(),
    require("postcss-input-range")(),
    require("autoprefixer")(),
    require("tailwindcss")(tailwindConfig),
    ...postcss,
    purge &&
      require("cssnano")({
        preset: "default"
      }),
    purge &&
      require("@fullhuman/postcss-purgecss")({
        content: ["./**/*.svelte"],
        extractors: [
          {
            extractor,
            extensions: ["svelte"]
          }
        ],
        whitelist: whitelist.filter(Boolean),
        whitelistPatterns: whitelistPatterns.filter(Boolean)
      })
  ].filter(Boolean);
};
