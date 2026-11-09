// Clean composited/AI sprites onto a true pixel grid with fast-pixelizer (the engine behind mono-pix, MIT).
// Usage: npm i fast-pixelizer pngjs && node art/snap.mjs
// For each composites/*_raw.png: take the 8x export, run snap() with output 'resized', require a 16x16 result,
// write originals-16/<id>.png and x8/<id>.png. Also records how snap() does on a soft-edged copy.
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath } from "node:url";
import { PNG } from "pngjs"; import { snap } from "fast-pixelizer";
const root = path.dirname(fileURLToPath(import.meta.url));
const read = (f) => PNG.sync.read(fs.readFileSync(f));
function blurUp(img, k) { // nearest 8x, then a 3x3 box blur: soft, anti-aliased cell edges like a fake pixel-art export
  const W = img.width * k, H = img.height * k, up = new Float32Array(W * H * 4), out = new Uint8ClampedArray(W * H * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let c = 0; c < 4; c++)
    up[(y * W + x) * 4 + c] = img.data[(Math.floor(y / k) * img.width + Math.floor(x / k)) * 4 + c];
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let c = 0; c < 4; c++) {
    let s = 0, n = 0;
    for (let dy = -1; dy <= 1; dy++) for (let dx = -1; dx <= 1; dx++) {
      const xx = x + dx, yy = y + dy; if (xx < 0 || yy < 0 || xx >= W || yy >= H) continue; s += up[(yy * W + xx) * 4 + c]; n++;
    }
    out[(y * W + x) * 4 + c] = s / n;
  }
  return { data: out, width: W, height: H };
}
function nearestUp(img, k) {
  const W = img.width * k, H = img.height * k, out = new Uint8ClampedArray(W * H * 4);
  for (let y = 0; y < H; y++) for (let x = 0; x < W; x++) for (let c = 0; c < 4; c++)
    out[(y * W + x) * 4 + c] = img.data[(Math.floor(y / k) * img.width + Math.floor(x / k)) * 4 + c];
  return { data: out, width: W, height: H };
}
function write(f, w, h, data, k = 1) {
  const png = new PNG({ width: w * k, height: h * k });
  for (let y = 0; y < h * k; y++) for (let x = 0; x < w * k; x++)
    for (let c = 0; c < 4; c++) png.data[(y * w * k + x) * 4 + c] = data[(Math.floor(y / k) * w + Math.floor(x / k)) * 4 + c];
  fs.writeFileSync(f, PNG.sync.write(png));
}
const report = {};
for (const f of fs.readdirSync(path.join(root, "composites")).filter((n) => n.endsWith("_raw.png"))) {
  const id = f.replace("_raw.png", ""); const src = read(path.join(root, "composites", f));
  // 1) Real pipeline: composites are edited as clean 8x exports, snap() must recover the 16x16 grid.
  const clean = nearestUp(src, 8);
  const r = snap(clean, { colorVariety: 32, output: "resized" });
  // 2) Stress test: soft-edged 8x (fake pixel art). Recorded only; see docs/references.md for the result.
  const soft = snap(blurUp(src, 8), { colorVariety: 32, output: "resized" });
  report[id] = { clean8x: [r.width, r.height], soft8x: [soft.width, soft.height], preservedSourceColors: r.preservedSourceColors };
  if (r.width !== 16 || r.height !== 16) { console.error(id, "snapped to", r.width, r.height); process.exitCode = 1; continue; }
  write(path.join(root, "originals-16", id + ".png"), 16, 16, r.data);
  write(path.join(root, "x8", id + ".png"), 16, 16, r.data, 8);
}
fs.writeFileSync(path.join(root, "composites", "snap-report.json"), JSON.stringify(report, null, 1));
console.log(report);
