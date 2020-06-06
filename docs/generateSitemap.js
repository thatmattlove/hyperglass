const fs = require("fs");

const globby = require("globby");
const prettier = require("prettier");

(async () => {
  const pages = await globby(["docs/**/*{.js,.mdx}"]);
  const sitemap = `
        <?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
            ${pages
              .map((page) => {
                const path = page
                  .replace("pages", "")
                  .replace(".js", "")
                  .replace(".mdx", "");
                const route = path === "/index" ? "" : path;
                console.log("Added entry to sitemap:", path, route);
                return `
                  <url>
                      <loc>${`https://hyperglass.io/${route}`}</loc>
                  </url>
              `;
              })
              .join("")}
        </urlset>
    `;

  const formatted = prettier.format(sitemap, {
    parser: "html",
  });

  fs.writeFileSync("static/sitemap.xml", formatted);
})();
