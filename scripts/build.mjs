import { cp, mkdir, rm } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const project = dirname(root);
const output = join(project, "dist");
const vendor = join(output, "vendor");

await rm(output, { recursive: true, force: true });
await mkdir(vendor, { recursive: true });
await cp(join(project, "index.html"), join(output, "index.html"));
await cp(join(project, "assets"), join(output, "assets"), { recursive: true });

const files = [
  ["react/umd/react.production.min.js", "react.production.min.js"],
  ["react-dom/umd/react-dom.production.min.js", "react-dom.production.min.js"],
  ["@babel/standalone/babel.min.js", "babel.min.js"],
  ["leaflet/dist/leaflet.css", "leaflet.css"],
  ["leaflet/dist/leaflet.js", "leaflet.js"],
  ["html2canvas/dist/html2canvas.min.js", "html2canvas.min.js"]
];

for (const [source, target] of files) {
  await cp(join(project, "node_modules", source), join(vendor, target));
}
