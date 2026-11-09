// Render FerVois FX samples from pixelfx (MIT, github.com/patch-gg/pixelfx) to PNG strips.
// Usage: git clone --depth 1 https://github.com/patch-gg/pixelfx /tmp/pixelfx && npm i pngjs
//        PIXELFX=/tmp/pixelfx node art/fx/render_fx.mjs
import fs from "node:fs"; import path from "node:path"; import { fileURLToPath, pathToFileURL } from "node:url";
import { PNG } from "pngjs";
const here = path.dirname(fileURLToPath(import.meta.url));
const PFX = process.env.PIXELFX || "/tmp/pixelfx";
const core = await import(pathToFileURL(path.join(PFX, "src/core/index.js")));
const FX = [
  ["projectiles/laser-bolt", "Laser bolt (Tinker rifles, Lumen Turret)", { palette: ["#062a2a","#0d4f5c","#14809a","#24c8d8","#4de8ff","#8af4ff","#d0fcff","#ffffff"] }],
  ["melee/sword-slash", "Sword slash (Knight)", {}],
  ["impacts/shield-block", "Shield block (Knight Bulwark)", {}],
  ["spawn/disintegrate", "Disintegrate (enemy defeat, no blood)", {}],
  ["spawn/coin-drop", "Coin drop (loot burst)", {}],
];
const BG = 0xff2a1e16; // ABGR of #161e2a
const out = [];
for (const [id, label, opts] of FX) {
  const mod = await import(pathToFileURL(path.join(PFX, "src/fx", id + ".js")));
  const [w, h] = mod.meta.size, [ox, oy] = mod.meta.origin ?? [w / 2, h / 2], D = mod.meta.duration ?? 1;
  const N = 6, png = new PNG({ width: w * N, height: h });
  const fx = core.createFx(mod, { x: ox, y: oy, ...opts });
  const frame = core.createFrame(w, h); const buf = new Uint8ClampedArray(w * h * 4);
  let t = 0;
  for (let k = 0; k < N; k++) {
    const target = (D * (k + 0.5)) / N; fx.update(target - t); t = target;
    core.clearFrame(frame); fx.draw(frame, "back"); fx.draw(frame, "front"); core.composite(frame, buf, BG);
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) for (let c = 0; c < 4; c++) png.data[(y * w * N + k * w + x) * 4 + c] = buf[(y * w + x) * 4 + c];
  }
  const file = id.replace("/", "--") + ".png";
  fs.writeFileSync(path.join(here, file), PNG.sync.write(png));
  out.push({ id, label, file, frameSize: [w, h], frames: N, duration: D });
}
fs.writeFileSync(path.join(here, "fx.json"), JSON.stringify(out, null, 1));
console.log(out.map((o) => o.file).join("\n"));
