// Minimale statische webserver voor outnest.eu — geen dependencies.
// Railway/Nixpacks pikt dit op via `npm start`.
const http = require("http");
const fs = require("fs");
const path = require("path");

const ROOT = __dirname;
const PORT = process.env.PORT || 3000;

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".ico": "image/x-icon",
  ".woff2": "font/woff2",
  ".xml": "application/xml; charset=utf-8",
  ".txt": "text/plain; charset=utf-8",
  ".json": "application/json; charset=utf-8",
};

// Fonts en afbeeldingen zijn content-hashed noch versioned, dus een dag cache
// is een veilige middenweg; HTML altijd vers zodat een deploy direct zichtbaar is.
function cacheFor(ext) {
  if (ext === ".html") return "no-cache";
  if (ext === ".woff2") return "public, max-age=31536000, immutable";
  return "public, max-age=86400";
}

const server = http.createServer((req, res) => {
  let pathname;
  try {
    pathname = decodeURIComponent(new URL(req.url, "http://x").pathname);
  } catch {
    res.writeHead(400).end("Bad request");
    return;
  }

  if (pathname === "/health") {
    res.writeHead(200, { "Content-Type": "text/plain" }).end("ok");
    return;
  }

  if (pathname.endsWith("/")) pathname += "index.html";

  // Voorkom dat een pad met ../ buiten de webroot wijst.
  const file = path.join(ROOT, pathname);
  if (!file.startsWith(ROOT + path.sep)) {
    res.writeHead(403).end("Forbidden");
    return;
  }
  // build/ bevat alleen bronbestanden voor het OG-plaatje, niet publiceren.
  if (path.relative(ROOT, file).split(path.sep)[0] === "build") {
    res.writeHead(404).end("Not found");
    return;
  }

  fs.readFile(file, (err, data) => {
    if (err) {
      // Eén pagina; alles wat niet bestaat valt terug op de homepage.
      fs.readFile(path.join(ROOT, "index.html"), (e2, home) => {
        if (e2) {
          res.writeHead(404, { "Content-Type": "text/plain" }).end("Not found");
        } else {
          res
            .writeHead(404, { "Content-Type": TYPES[".html"], "Cache-Control": "no-cache" })
            .end(home);
        }
      });
      return;
    }
    const ext = path.extname(file).toLowerCase();
    res.writeHead(200, {
      "Content-Type": TYPES[ext] || "application/octet-stream",
      "Cache-Control": cacheFor(ext),
      "X-Content-Type-Options": "nosniff",
      "X-Frame-Options": "SAMEORIGIN",
      "Referrer-Policy": "strict-origin-when-cross-origin",
      "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    });
    res.end(data);
  });
});

server.listen(PORT, () => console.log("outnest-site listening on " + PORT));
