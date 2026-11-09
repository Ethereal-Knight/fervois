"""Derive 64x64 FerVois character sprites from the 16x16 atlas originals.

Not a nearest-neighbor blow-up. Steps per sprite:
 1. Scale4x (EPX / Scale2x run twice) on exact colors: smooth diagonals, no new blended colors.
 2. Outline rebuild: the 4 px dark outer band from the 16 px outline is thinned to a 1 px outline,
    tinted 18% toward the color it touches (selective outline); the freed band takes the nearest inner color.
 3. Interior dark lines: long thin dark components (over 24 px) are thinned to 2 px, large dark masses are
    tinted 28% toward the surrounding color; small dark components (eyes, slits, buttons) stay pure.
 4. Material groups by tolerant flood fill (neighbor difference under 46, seed difference under 80), then
    shading per group with light from the top left: 1 px highlight on lit edges, shadow on far edges, a checker
    dither step in big groups, a glint on large metal. Hue steps are clamped to +/-0.035 so shadows never swing
    through magenta; greys get a fixed warm light and cool shadow tint.
Usage: python art/upscale64.py   (reads art/originals-16/*.png, writes art/x64/*.png and art/x64/report.json)
"""
import os, json, colorsys
from collections import deque
from PIL import Image

R = os.path.dirname(os.path.abspath(__file__))

def scale2x(px, w, h):
    out = [[None] * (w * 2) for _ in range(h * 2)]
    g = lambda x, y: px[min(h - 1, max(0, y))][min(w - 1, max(0, x))]
    for y in range(h):
        for x in range(w):
            P = px[y][x]; A = g(x, y - 1); B = g(x + 1, y); C = g(x - 1, y); D = g(x, y + 1)
            e0 = e1 = e2 = e3 = P
            if C == A and C != D and A != B: e0 = A
            if A == B and A != C and B != D: e1 = B
            if D == C and D != B and C != A: e2 = C
            if B == D and B != A and D != C: e3 = D
            out[2 * y][2 * x], out[2 * y][2 * x + 1], out[2 * y + 1][2 * x], out[2 * y + 1][2 * x + 1] = e0, e1, e2, e3
    return out

def lum(c): return (0.299 * c[0] + 0.587 * c[1] + 0.114 * c[2]) / 255
def hsv(c): return colorsys.rgb_to_hsv(c[0] / 255, c[1] / 255, c[2] / 255)
def rgb(h, s, v): return tuple(int(round(max(0, min(1, k)) * 255)) for k in colorsys.hsv_to_rgb(h % 1, s, v)) + (255,)
def shift(c, dv, dh, ds):
    """Hue-shifted ramp step: lights lean warm yellow, shadows lean cool blue. Greys get a fixed tint."""
    h, s, v = hsv(c)
    target = 0.13 if dv > 0 else 0.64
    if s < 0.15:
        return rgb(target, s * 0.6 + (0.03 if dv > 0 else 0.10), v + dv)
    dhh = ((target - h + 0.5) % 1) - 0.5
    step = max(-0.035, min(0.035, dhh * dh))  # small hue steps only, never swing through magenta
    return rgb(h + step, min(1, max(0, s + ds)), v + dv)
def mix(a, b, t): return tuple(int(a[i] * (1 - t) + b[i] * t) for i in range(3)) + (255,)

def process(src):
    im = Image.open(src).convert("RGBA"); w, h = im.size
    px = [[(lambda p: p if p[3] >= 128 else None)(im.getpixel((x, y))) for x in range(w)] for y in range(h)]
    px = [[(p[0], p[1], p[2], 255) if p else None for p in row] for row in px]
    big = scale2x(*[scale2x(px, w, h), w * 2, h * 2]); W, H = w * 4, h * 4
    inside = lambda x, y: 0 <= x < W and 0 <= y < H and big[y][x] is not None
    dark = lambda c: c is not None and lum(c) < 0.16
    # distance to background (4-neighbor BFS)
    dist = [[0 if big[y][x] is None else 99 for x in range(W)] for y in range(H)]
    q = deque((x, y) for y in range(H) for x in range(W) if big[y][x] is None)
    for y in range(H):
        for x in (0, W - 1):
            if big[y][x] is not None and dist[y][x] > 1: dist[y][x] = 1
    for x in range(W):
        for y in (0, H - 1):
            if big[y][x] is not None and dist[y][x] > 1: dist[y][x] = 1
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and dist[Y][X] > dist[y][x] + 1: dist[Y][X] = dist[y][x] + 1; q.append((X, Y))
    # nearest non-dark interior color for every pixel (multi-source BFS)
    near = [[None] * W for _ in range(H)]
    q = deque()
    for y in range(H):
        for x in range(W):
            if big[y][x] is not None and not dark(big[y][x]): near[y][x] = big[y][x]; q.append((x, y))
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and big[Y][X] is not None and near[Y][X] is None: near[Y][X] = near[y][x]; q.append((X, Y))
    outline_base = min((c for row in big for c in row if c is not None), key=lum)
    outline_base = mix(outline_base, (20, 16, 26), 0.6)
    base = [[None] * W for _ in range(H)]; is_out = [[False] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            c = big[y][x]
            if c is None: continue
            if dist[y][x] == 1:
                is_out[y][x] = True
            elif dark(c) and dist[y][x] <= 4 and near[y][x] is not None:
                base[y][x] = shift(near[y][x], -0.10, 0.25, 0.04) if dist[y][x] == 2 else near[y][x]  # freed band
            else:
                base[y][x] = c
    # thin long interior dark lines (4 px after Scale4x) to 2 px; keep eyes, slits and big dark areas
    dd = [[0 if (base[y][x] is None or not dark(base[y][x])) else 99 for x in range(W)] for y in range(H)]
    q = deque((x, y) for y in range(H) for x in range(W) if dd[y][x] == 0)
    while q:
        x, y = q.popleft()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            X, Y = x + dx, y + dy
            if 0 <= X < W and 0 <= Y < H and dd[Y][X] > dd[y][x] + 1: dd[Y][X] = dd[y][x] + 1; q.append((X, Y))
    seen = [[False] * W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            if dd[y][x] in (0, 99) or seen[y][x] or base[y][x] is None: continue
            comp = []; q = deque([(x, y)]); seen[y][x] = True
            while q:
                a, b = q.popleft(); comp.append((a, b))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = a + dx, b + dy
                    if 0 <= X < W and 0 <= Y < H and not seen[Y][X] and 0 < dd[Y][X] < 99 and base[Y][X] is not None:
                        seen[Y][X] = True; q.append((X, Y))
            if len(comp) <= 24: continue  # eyes, slits, buttons stay pure dark
            if max(dd[b][a] for a, b in comp) <= 2:
                for a, b in comp:
                    if dd[b][a] == 2 and near[b][a] is not None: base[b][a] = shift(near[b][a], -0.10, 0.25, 0.04)
            else:  # big dark mass: keep a 1 px dark edge, tint the inside toward what surrounds it (deep shadow, not a hole)
                for a, b in comp:
                    if dd[b][a] >= 2 and near[b][a] is not None and dist[b][a] > 1: base[b][a] = mix(base[b][a], near[b][a], 0.28)
    # material groups: flood fill with a color tolerance so the source's own shading stays inside one group
    def cd(p, q): return sum((p[i] - q[i]) ** 2 for i in range(3)) ** 0.5
    lab = [[-1] * W for _ in range(H)]; regions = []
    for y in range(H):
        for x in range(W):
            if base[y][x] is None or lab[y][x] >= 0: continue
            k = len(regions); cells = []; q = deque([(x, y)]); lab[y][x] = k; seed = base[y][x]
            while q:
                a, b = q.popleft(); cells.append((a, b))
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    X, Y = a + dx, b + dy
                    if 0 <= X < W and 0 <= Y < H and lab[Y][X] < 0 and base[Y][X] is not None and cd(base[Y][X], base[b][a]) < 46 and cd(base[Y][X], seed) < 80:
                        lab[Y][X] = k; q.append((X, Y))
            regions.append(cells)
    out = [[base[y][x] for x in range(W)] for y in range(H)]
    same = lambda x, y, k: 0 <= x < W and 0 <= y < H and lab[y][x] == k
    for k, cells in enumerate(regions):
        if len(cells) < 24: continue
        for (x, y) in cells:
            c = base[y][x]
            if dark(c): continue
            lit = not same(x - 1, y, k) or not same(x, y - 1, k)
            far1 = not same(x + 1, y, k) or not same(x, y + 1, k)
            far2 = not same(x + 2, y, k) or not same(x, y + 2, k)
            if far1 and not lit: out[y][x] = shift(c, -0.15, 0.3, 0.05)
            elif far2 and not lit and len(cells) >= 60 and (x + y) % 2 == 0: out[y][x] = shift(c, -0.09, 0.2, 0.03)
            elif lit and not far1: out[y][x] = shift(c, 0.12, 0.2, -0.05)
        cs = [base[y][x] for x, y in cells]; avg = tuple(sum(p[i] for p in cs) // len(cs) for i in range(3))
        hh, ss, vv = hsv(avg)
        if ss < 0.3 and vv > 0.45 and len(cells) >= 60:  # glint on big metal plates
            for (x, y) in sorted(cells, key=lambda p: p[0] + p[1])[4:6]:
                out[y][x] = shift(base[y][x], 0.3, 0.1, -0.2)
    # selective 1 px outline
    for y in range(H):
        for x in range(W):
            if not is_out[y][x]: continue
            nb = [out[Y][X] for X, Y in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if inside(X, Y) and not is_out[Y][X] and out[Y][X]]
            t = mix(outline_base, nb[0], 0.18) if nb else outline_base
            out[y][x] = t
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for y in range(H):
        for x in range(W):
            if out[y][x]: img.putpixel((x, y), out[y][x])
    return img

if __name__ == "__main__":
    os.makedirs(os.path.join(R, "x64"), exist_ok=True); rep = {}
    for f in sorted(os.listdir(os.path.join(R, "originals-16"))):
        if not f.endswith(".png"): continue
        img = process(os.path.join(R, "originals-16", f)); img.save(os.path.join(R, "x64", f))
        rep[f[:-4]] = {"size": img.size, "colors": len(set(img.get_flattened_data())) - 1}
    json.dump(rep, open(os.path.join(R, "x64", "report.json"), "w"), indent=1); print(len(rep), "sprites")
