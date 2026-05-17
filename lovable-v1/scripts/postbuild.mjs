// Post-build script: create dist/client/index.html for static hosting (Vercel, etc.)
// This generates the SPA entry point from the hashed client assets.
import { readdirSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const assetsDir = join(import.meta.dirname, "..", "dist", "client", "assets");

const files = readdirSync(assetsDir);
const jsFile = files.find((f) => f.startsWith("index-") && f.endsWith(".js"));
const cssFile = files.find((f) => f.startsWith("styles-") && f.endsWith(".css"));

if (!jsFile) {
  console.error("ERROR: Could not find client entry JS in dist/client/assets/");
  process.exit(1);
}

const html = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>ReviewResponseAssistant · 审稿意见回复助手</title>
  ${cssFile ? `<link rel="stylesheet" href="/assets/${cssFile}" />` : ""}
  <style>body { margin: 0; background: oklch(0.98 0.008 85); }</style>
</head>
<body>
  <div id="root"></div>
  <script type="module" src="/assets/${jsFile}"></script>
</body>
</html>`;

const outPath = join(import.meta.dirname, "..", "dist", "client", "index.html");
writeFileSync(outPath, html);
console.log("Generated dist/client/index.html for static deployment");
