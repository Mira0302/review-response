import { readdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const assetsDir = join("dist", "client", "assets");

// Find hashed CSS and entry JS files
const files = readdirSync(assetsDir);
const cssFile = files.find((f) => f.startsWith("styles-") && f.endsWith(".css"));

// Pick the largest index-*.js as the main entry (not route chunks)
const jsCandidates = files.filter((f) => f.startsWith("index-") && f.endsWith(".js"));
const jsFile = jsCandidates.length === 1
  ? jsCandidates[0]
  : jsCandidates.reduce((a, b) =>
      (statSync(join(assetsDir, a)).size > statSync(join(assetsDir, b)).size) ? a : b
    );

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
  ${jsFile ? `<script type="module" src="/assets/${jsFile}"></script>` : ""}
</body>
</html>
`;

const outPath = join("dist", "client", "index.html");
writeFileSync(outPath, html);
console.log(`Generated ${outPath}`);
