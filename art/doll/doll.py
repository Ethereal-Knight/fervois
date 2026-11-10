"""FerVois paper doll: 64x64 base body + equipment layers, drawn procedurally as material masks.

Each layer is a 64x64 grid of material ids (0 = empty). A palette maps every material to a base color; the
renderer builds a 3-step ramp per material (highlight, base, shadow), shades each material region with light
from the top left, and gives every layer its own 1 px tinted dark outline. Recolor = swap the palette
(palette-swap / tint mask), the mask never changes.

Views: down (front), up (back), left (side). right = mirror of left.
Usage: python art/doll/doll.py  -> art/doll/layers/<slot>/<item>_<view>.png, art/doll/combos/*.png, art/doll/doll.json

Full idle/walk/attack sheets (8 x 12) live in art/doll/sheets.py:
    python art/doll/sheets.py
"""
import os, json, colorsys
from PIL import Image

R = os.path.dirname(os.path.abspath(__file__)); N = 64
VIEWS = ["down", "up", "left"]
# materials
SKIN, HAIR, EYE, CLOTH, CLOTH2, METAL, TRIM, LEATHER, WOOD, ACCENT, WHITE, GEM = range(1, 13)

def grid(): return [[0] * N for _ in range(N)]
def rect(g, x0, y0, x1, y1, m):
    for y in range(max(0, y0), min(N, y1 + 1)):
        for x in range(max(0, x0), min(N, x1 + 1)): g[y][x] = m
def ell(g, cx, cy, rx, ry, m, y_min=-99, y_max=99):
    for y in range(N):
        for x in range(N):
            if ((x - cx + 0.5) / rx) ** 2 + ((y - cy + 0.5) / ry) ** 2 <= 1 and y_min <= y <= y_max: g[y][x] = m
def line(g, x0, y0, x1, y1, m, w=1):
    n = max(abs(x1 - x0), abs(y1 - y0), 1)
    for i in range(n + 1):
        x = round(x0 + (x1 - x0) * i / n); y = round(y0 + (y1 - y0) * i / n)
        rect(g, x - w // 2, y - w // 2, x + (w - 1) // 2, y + (w - 1) // 2, m)
def clear(g, x0, y0, x1, y1): rect(g, x0, y0, x1, y1, 0)
def mirror(g): return [list(reversed(r)) for r in g]

# ---- anchors (shared by every layer, documented in docs/systems/paper-doll.md)
A = {"head": (32, 19), "neck": (32, 30), "chest": (32, 37), "hip": (32, 46), "feet_y": 60,
     "hand_main": {"down": (19, 45), "up": (45, 45), "left": (27, 44)},
     "hand_off": {"down": (45, 45), "up": (19, 45), "left": (37, 43)}}

# ---------------- base body
def body(view):
    g = grid()
    if view in ("down", "up"):
        rect(g, 25, 46, 30, 57, SKIN); rect(g, 34, 46, 39, 57, SKIN)          # legs
        rect(g, 24, 57, 30, 60, LEATHER); rect(g, 34, 57, 40, 60, LEATHER)    # bare feet wraps
        rect(g, 23, 31, 41, 47, CLOTH)                                          # undershirt
        rect(g, 17, 32, 22, 44, SKIN); rect(g, 42, 32, 47, 44, SKIN)          # arms
        ell(g, 19.5, 46, 3, 3, SKIN); ell(g, 44.5, 46, 3, 3, SKIN)            # hands
        rect(g, 29, 28, 35, 31, SKIN)                                           # neck
        ell(g, 32, 19, 12, 11, SKIN)                                            # head
        if view == "down":
            rect(g, 26, 19, 27, 22, EYE); rect(g, 37, 19, 38, 22, EYE); g[19][26] = WHITE; g[19][37] = WHITE
            rect(g, 31, 25, 33, 25, CLOTH2)                                     # mouth hint
    else:  # left (side)
        rect(g, 28, 46, 32, 57, SKIN); rect(g, 33, 46, 36, 56, SKIN)
        rect(g, 25, 57, 32, 60, LEATHER); rect(g, 31, 56, 37, 59, LEATHER)
        rect(g, 27, 31, 38, 47, CLOTH)
        rect(g, 29, 32, 33, 43, SKIN); ell(g, 28, 44.5, 3, 3, SKIN)            # front arm
        rect(g, 30, 28, 35, 31, SKIN)
        ell(g, 32, 19, 11, 11, SKIN)
        rect(g, 24, 19, 25, 22, EYE); g[19][24] = WHITE; rect(g, 20, 21, 21, 22, SKIN)  # eye, nose
    return g

def hair(view, style="short"):
    g = grid()
    if view == "down":
        ell(g, 32, 15, 12.5, 8, HAIR, y_max=16); rect(g, 20, 14, 22, 21, HAIR); rect(g, 42, 14, 44, 21, HAIR)
        if style == "long": rect(g, 19, 14, 22, 30, HAIR); rect(g, 42, 14, 45, 30, HAIR)
    elif view == "up":
        ell(g, 32, 18, 12.5, 11.5, HAIR)
        if style == "long": rect(g, 21, 18, 43, 33, HAIR)
    else:
        ell(g, 34, 15, 11.5, 8, HAIR, y_max=17); rect(g, 36, 14, 43, 25, HAIR)
        if style == "long": rect(g, 37, 14, 43, 33, HAIR)
    return g

# ---------------- equipment layers: each returns a mask for a view
def head_helm(view, plume=True):
    g = grid()
    if view == "left":
        ell(g, 32, 18, 12.5, 12.5, METAL); rect(g, 19, 18, 26, 21, EYE); rect(g, 30, 27, 44, 30, TRIM)
        rect(g, 32, 5, 33, 30, TRIM)
        if plume: ell(g, 38, 5, 7, 3.5, CLOTH2)
    else:
        ell(g, 32, 18, 13, 12.5, METAL); rect(g, 19, 27, 45, 30, TRIM)
        if view == "down": rect(g, 23, 18, 41, 21, EYE); rect(g, 31, 18, 33, 26, METAL); rect(g, 31, 6, 33, 15, TRIM)
        else: rect(g, 31, 6, 33, 28, TRIM)
        if plume: ell(g, 34, 5, 6, 4, CLOTH2)
    return g
def head_hood(view):
    g = grid()
    if view == "left":
        ell(g, 33, 18, 13, 13, CLOTH); clear(g, 18, 13, 28, 27); ell(g, 29, 20, 8, 8, 0); rect(g, 37, 28, 46, 34, CLOTH)
    else:
        ell(g, 32, 18, 13.5, 13, CLOTH); rect(g, 20, 26, 44, 33, CLOTH)
        if view == "down": ell(g, 32, 21, 9, 8.5, 0); rect(g, 30, 29, 34, 33, CLOTH2)
    return g
def head_wizard(view):
    g = grid()
    if view == "left":
        rect(g, 17, 13, 47, 15, CLOTH); line(g, 26, 13, 34, -1, CLOTH, 9); line(g, 30, 12, 40, 2, CLOTH, 5); rect(g, 22, 10, 42, 12, CLOTH2)
    else:
        rect(g, 16, 13, 48, 15, CLOTH)
        for y in range(0, 13): rect(g, 32 - (13 - y) // 1 + 4, y, 32 + (13 - y) // 1 - 4, y, CLOTH)
        rect(g, 22, 10, 42, 12, CLOTH2); ell(g, 32, 3, 2, 2, ACCENT)
    return g
def head_goggles(view):
    g = grid()
    if view == "left":
        ell(g, 34, 14, 12, 7, LEATHER, y_max=14); rect(g, 22, 12, 46, 13, LEATHER); ell(g, 25, 12, 3.5, 3, ACCENT); rect(g, 22, 15, 46, 15, TRIM)
    else:
        ell(g, 32, 13, 13, 7, LEATHER, y_max=14); rect(g, 19, 15, 45, 15, TRIM)
        if view == "down": ell(g, 27, 13, 4, 3.5, ACCENT); ell(g, 37, 13, 4, 3.5, ACCENT); rect(g, 31, 12, 33, 13, TRIM)
    return g

def chest_plate(view):
    g = grid()
    if view == "left":
        rect(g, 26, 31, 39, 47, METAL); rect(g, 26, 44, 39, 47, TRIM); ell(g, 31, 34, 5, 4, METAL); rect(g, 37, 33, 39, 44, TRIM)
    else:
        rect(g, 22, 31, 42, 47, METAL); rect(g, 22, 44, 42, 47, TRIM); ell(g, 19.5, 33, 5.5, 4.5, METAL); ell(g, 44.5, 33, 5.5, 4.5, METAL)
        if view == "down": rect(g, 31, 32, 33, 43, TRIM); rect(g, 26, 38, 38, 38, TRIM)
    return g
def chest_robe(view):
    g = grid()
    if view == "left":
        for y in range(31, 59): w = 6 + (y - 31) // 3; rect(g, 32 - w, y, 32 + w - 2, y, CLOTH)
        rect(g, 29, 31, 33, 43, CLOTH); rect(g, 22, 56, 40, 58, CLOTH2)
    else:
        for y in range(31, 59): w = 10 + (y - 31) // 3; rect(g, 32 - w, y, 32 + w - 1, y, CLOTH)
        rect(g, 17, 32, 22, 43, CLOTH); rect(g, 42, 32, 47, 43, CLOTH); rect(g, 18, 56, 46, 58, CLOTH2)
        if view == "down": rect(g, 31, 31, 33, 58, CLOTH2); rect(g, 22, 45, 42, 46, TRIM)
    return g
def chest_vest(view):
    g = grid()
    if view == "left": rect(g, 26, 31, 39, 47, LEATHER); rect(g, 26, 43, 39, 44, TRIM); line(g, 28, 31, 38, 43, CLOTH2, 2)
    else:
        rect(g, 22, 31, 42, 47, LEATHER); rect(g, 22, 43, 42, 44, TRIM)
        if view == "down": rect(g, 30, 31, 34, 42, CLOTH); line(g, 23, 32, 40, 46, CLOTH2, 2)
    return g
def chest_coat(view):
    g = grid()
    if view == "left": rect(g, 25, 31, 40, 52, CLOTH); rect(g, 29, 32, 33, 44, CLOTH); rect(g, 25, 44, 40, 45, TRIM)
    else:
        rect(g, 21, 31, 43, 52, CLOTH); rect(g, 17, 32, 22, 44, CLOTH); rect(g, 42, 32, 47, 44, CLOTH); rect(g, 21, 44, 43, 45, TRIM)
        if view == "down": rect(g, 31, 31, 33, 52, CLOTH2); g[36][29] = g[40][29] = TRIM; g[36][35] = g[40][35] = TRIM
    return g

def legs_greaves(view):
    g = grid()
    if view == "left": rect(g, 27, 46, 33, 57, METAL); rect(g, 33, 46, 37, 56, TRIM); rect(g, 27, 50, 33, 51, TRIM)
    else: rect(g, 24, 46, 31, 57, METAL); rect(g, 33, 46, 40, 57, METAL); rect(g, 24, 50, 31, 51, TRIM); rect(g, 33, 50, 40, 51, TRIM)
    return g
def legs_trousers(view):
    g = grid()
    if view == "left": rect(g, 27, 46, 33, 57, CLOTH); rect(g, 33, 46, 37, 56, CLOTH2)
    else: rect(g, 24, 46, 31, 57, CLOTH); rect(g, 33, 46, 40, 57, CLOTH)
    return g
def feet_sabatons(view):
    g = grid()
    if view == "left": rect(g, 23, 56, 33, 61, METAL); rect(g, 31, 55, 38, 60, TRIM)
    else: rect(g, 23, 56, 31, 61, METAL); rect(g, 33, 56, 41, 61, METAL); rect(g, 23, 60, 41, 61, TRIM); clear(g, 32, 56, 32, 61)
    return g
def feet_boots(view):
    g = grid()
    if view == "left": rect(g, 24, 54, 33, 61, LEATHER); rect(g, 31, 54, 37, 60, LEATHER); rect(g, 24, 60, 33, 61, TRIM)
    else: rect(g, 24, 54, 31, 61, LEATHER); rect(g, 33, 54, 40, 61, LEATHER); rect(g, 24, 60, 40, 61, TRIM)
    return g
def hands_gauntlets(view, mat=METAL):
    g = grid()
    if view == "left": ell(g, 28, 44.5, 3.5, 3.5, mat); rect(g, 28, 40, 33, 42, TRIM)
    else: ell(g, 19.5, 46, 3.5, 3.5, mat); ell(g, 44.5, 46, 3.5, 3.5, mat); rect(g, 17, 41, 22, 43, TRIM); rect(g, 42, 41, 47, 43, TRIM)
    return g
def back_cape(view):
    g = grid()
    if view == "down":
        for y in range(30, 56): w = 12 + (y - 30) // 4; rect(g, 32 - w, y, 32 + w - 1, y, CLOTH)
    elif view == "up":
        for y in range(29, 57): w = 11 + (y - 29) // 3; rect(g, 32 - w, y, 32 + w - 1, y, CLOTH)
        rect(g, 22, 29, 42, 31, CLOTH2)
    else:
        for y in range(30, 55): w = 3 + (y - 30) // 3; rect(g, 39, y, 39 + w, y, CLOTH)
    return g

def main_sword(view, laser=False):
    g = grid(); bx, by = A["hand_main"][view]
    blade = ACCENT if laser else METAL
    if view == "left": line(g, bx - 1, by - 2, bx - 12, by - 24, blade, 3); rect(g, bx - 4, by - 3, bx + 2, by - 2, TRIM); rect(g, bx - 1, by - 1, bx, by + 2, LEATHER)
    else: rect(g, bx - 1, by - 27, bx + 1, by - 4, blade); rect(g, bx - 4, by - 4, bx + 4, by - 3, TRIM); rect(g, bx - 1, by - 2, bx + 1, by + 2, LEATHER); g[by - 28][bx] = blade
    return g
def main_staff(view, orb=ACCENT):
    g = grid(); bx, by = A["hand_main"][view]
    rect(g, bx - 1, by - 30, bx, by + 12, WOOD); ell(g, bx, by - 32, 3.5, 3.5, orb)
    return g
def main_pistol(view):
    g = grid(); bx, by = A["hand_main"][view]
    if view == "left": rect(g, bx - 12, by - 3, bx, by - 1, METAL); rect(g, bx - 2, by - 1, bx, by + 3, WOOD); rect(g, bx - 13, by - 3, bx - 12, by - 1, ACCENT)
    else: rect(g, bx - 1, by - 10, bx + 1, by, METAL); rect(g, bx - 2, by, bx + 2, by + 3, WOOD); rect(g, bx - 1, by - 11, bx + 1, by - 10, ACCENT)
    return g
def main_bow(view):
    g = grid(); bx, by = A["hand_main"][view]
    if view == "left":
        for y in range(by - 16, by + 12): x = bx - 4 - round(4 * (1 - ((y - by + 2) / 14) ** 2)); g[y][x] = WOOD; g[y][x - 1] = WOOD
        line(g, bx - 4, by - 16, bx - 4, by + 11, WHITE, 1)
    else:
        for y in range(by - 18, by + 12): x = bx - round(5 * (1 - ((y - by + 3) / 15) ** 2)); g[y][x] = WOOD; g[y][x + 1] = WOOD
        line(g, bx + 1, by - 18, bx + 1, by + 11, WHITE, 1)
    return g
def off_shield(view):
    g = grid(); bx, by = A["hand_off"][view]
    if view == "left": rect(g, bx - 2, by - 9, bx + 2, by + 7, TRIM); rect(g, bx - 1, by - 8, bx + 1, by + 6, METAL)
    else:
        rect(g, bx - 6, by - 10, bx + 6, by + 4, METAL); ell(g, bx, by + 4, 6.5, 5, METAL, y_min=by + 4)
        for d in range(0, 13): g[by - 10][bx - 6 + d] = TRIM
        rect(g, bx - 1, by - 7, bx + 1, by + 5, CLOTH2); rect(g, bx - 4, by - 3, bx + 4, by - 1, CLOTH2)
    return g
def off_tome(view):
    g = grid(); bx, by = A["hand_off"][view]
    rect(g, bx - 4, by - 5, bx + 4, by + 3, CLOTH2); rect(g, bx - 3, by - 4, bx + 3, by + 2, WHITE); rect(g, bx - 4, by - 1, bx + 4, by - 1, ACCENT)
    return g
def off_lantern(view):
    g = grid(); bx, by = A["hand_off"][view]
    rect(g, bx, by, bx, by + 3, TRIM); rect(g, bx - 3, by + 3, bx + 3, by + 11, TRIM); rect(g, bx - 2, by + 4, bx + 2, by + 10, ACCENT)
    return g

ITEMS = {
 "head": {"helm": head_helm, "helm_plain": lambda v: head_helm(v, False), "hood": head_hood, "wizard_hat": head_wizard, "goggles": head_goggles},
 "chest": {"plate": chest_plate, "robe": chest_robe, "vest": chest_vest, "coat": chest_coat},
 "legs": {"greaves": legs_greaves, "trousers": legs_trousers},
 "feet": {"sabatons": feet_sabatons, "boots": feet_boots},
 "hands": {"gauntlets": hands_gauntlets, "gloves": lambda v: hands_gauntlets(v, LEATHER)},
 "back": {"cape": back_cape},
 "main": {"sword": main_sword, "lumen_blade": lambda v: main_sword(v, True), "staff": main_staff, "pistol": main_pistol, "bow": main_bow},
 "off": {"shield": off_shield, "tome": off_tome, "lantern": off_lantern},
}
# draw order per view (first = bottom). Back faces flip cape and arms-side items.
ORDER = {
 "down": ["back", "body", "hair", "legs", "feet", "chest", "hands", "head", "off", "main"],
 "up":   ["main", "off", "body", "hair", "legs", "feet", "chest", "hands", "head", "back"],
 "left": ["off", "back", "body", "hair", "legs", "feet", "chest", "hands", "head", "main"],
}
# Head pieces that cover the hair layer. mail_coif matches the open-face rule used by the sheet baker.
HIDES_HAIR = ("helm", "helm_plain", "hood", "mail_coif")

# ---------------- palettes (tint masks: material -> base color)
def H(c): return tuple(int(c[i:i + 2], 16) for i in (1, 3, 5))
BASE_PAL = {SKIN: "#E8B48A", HAIR: "#6B3E22", EYE: "#1A1420", CLOTH: "#8A6A48", CLOTH2: "#5B3B2A", METAL: "#9AA4B5", TRIM: "#5A6274",
            LEATHER: "#7A4E2C", WOOD: "#8C5A2E", ACCENT: "#40E8FF", WHITE: "#F2EEE2", GEM: "#F2789B"}
def pal(**kw):
    p = dict(BASE_PAL)
    for k, v in kw.items(): p[globals()[k.upper()]] = v
    return p

def hsv(c): return colorsys.rgb_to_hsv(*(k / 255 for k in c))
def rgb(h, s, v): return tuple(int(round(max(0, min(1, k)) * 255)) for k in colorsys.hsv_to_rgb(h % 1, max(0, min(1, s)), v))
def ramp(c):
    h, s, v = hsv(c)
    def hs(target, amt):
        d = ((target - h + 0.5) % 1) - 0.5; return h + max(-0.035, min(0.035, d * amt))
    if s < 0.15: return rgb(0.12, s * 0.6 + 0.03, v + 0.14), c, rgb(0.64, s * 0.6 + 0.10, v - 0.16), rgb(0.66, s * 0.6 + 0.14, v - 0.28)
    return rgb(hs(0.13, 0.25), s - 0.06, v + 0.12), c, rgb(hs(0.64, 0.3), s + 0.06, v - 0.16), rgb(hs(0.66, 0.4), s + 0.08, v - 0.28)

def render(mask, palette, outline=True):
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0)); px = img.load()
    M = lambda x, y: mask[y][x] if 0 <= x < N and 0 <= y < N else 0
    for y in range(N):
        for x in range(N):
            m = mask[y][x]
            if not m: continue
            c = H(palette[m]); hi, base, sh, sh2 = ramp(c)
            if m in (EYE, WHITE): px[x, y] = c + (255,); continue
            lit = M(x - 1, y) != m or M(x, y - 1) != m
            far1 = M(x + 1, y) != m or M(x, y + 1) != m
            far2 = M(x + 2, y) != m or M(x, y + 2) != m
            col = base
            if far1 and not lit: col = sh2 if m in (METAL, TRIM) else sh
            elif far2 and not lit and (x + y) % 2 == 0: col = sh
            elif lit and not far1: col = hi
            px[x, y] = col + (255,)
    # glint on metal: first two lit metal pixels along the top-left diagonal of each metal blob row
    if outline:
        out = img.copy(); op = out.load()
        for y in range(N):
            for x in range(N):
                if mask[y][x]: continue
                nb = [mask[Y][X] for X, Y in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if 0 <= X < N and 0 <= Y < N and mask[Y][X]]
                if nb:
                    c = H(palette[nb[0]]); d = (22, 17, 28)
                    op[x, y] = tuple(int(d[i] * 0.8 + c[i] * 0.2) for i in range(3)) + (255,)
        img = out
    return img

def layer_mask(slot, item, view):
    if view == "right": return mirror(layer_mask(slot, item, "left"))
    return ITEMS[slot][item](view)

def composite(loadout, palette, view="down", aura=None):
    """loadout: {slot: item}. 'body' and 'hair' are always present (hair can be None)."""
    order = ORDER["left" if view == "right" else view]
    if view == "right": order = ORDER["left"]
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    for slot in order:
        if slot == "body": m = body("left" if view == "right" else view)
        elif slot == "hair":
            if not loadout.get("hair") or loadout.get("head") in HIDES_HAIR: continue
            m = hair("left" if view == "right" else view, loadout["hair"])
        else:
            it = loadout.get(slot)
            if not it: continue
            m = ITEMS[slot][it]("left" if view == "right" else view)
        if view == "right": m = mirror(m)
        lp = palette.get(slot, palette["*"])
        img.alpha_composite(render(m, lp))
    if aura:
        src = img.copy(); s = src.load(); p = img.load()
        for y in range(N):
            for x in range(N):
                if s[x, y][3]: continue
                if any(0 <= x + dx < N and 0 <= y + dy < N and s[x + dx, y + dy][3] for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))): p[x, y] = H(aura) + (255,)
    return img

def exploded(loadout, palette, view="down"):
    """[(slot, item, RGBA image)] in draw order, one image per layer that is drawn. Used by the Paper doll page."""
    res = []; v = "left" if view == "right" else view
    for slot in ORDER[v]:
        if slot == "body": m, it = body(v), "base"
        elif slot == "hair":
            if not loadout.get("hair") or loadout.get("head") in HIDES_HAIR: continue
            m, it = hair(v, loadout["hair"]), loadout["hair"]
        else:
            it = loadout.get(slot)
            if not it: continue
            m = ITEMS[slot][it](v)
        if view == "right": m = mirror(m)
        res.append((slot, it, render(m, palette.get(slot, palette["*"]))))
    return res

def anchor_chart(scale=6):
    """Base body on the 64x64 grid with 8 px guides and anchor markers."""
    from PIL import ImageDraw
    im = Image.new("RGBA", (N * scale, N * scale), (28, 34, 48, 255))
    im.alpha_composite(render(body("down"), BASE_PAL).resize((N * scale, N * scale), Image.NEAREST))
    d = ImageDraw.Draw(im)
    for k in range(0, N + 1, 8):
        c = (64, 232, 255, 90) if k % 32 else (64, 232, 255, 200)
        d.line([(k * scale, 0), (k * scale, N * scale)], fill=c); d.line([(0, k * scale), (N * scale, k * scale)], fill=c)
    pts = [A["head"], A["neck"], A["chest"], A["hip"], A["hand_main"]["down"], A["hand_off"]["down"], (32, A["feet_y"])]
    cols = [(242, 179, 61), (242, 120, 155), (242, 120, 155), (242, 120, 155), (255, 122, 46), (186, 85, 255), (110, 154, 69)]
    for (x, y), c in zip(pts, cols):
        cx, cy = x * scale + scale // 2, y * scale + scale // 2
        d.rectangle([cx - scale, cy - scale, cx + scale, cy + scale], outline=c + (255,), width=2)
    return im

# ---------------- class tiers as loadouts (palette per tier)
STEEL = pal(cloth="#4A5878", cloth2="#C8372E"); GOLDP = pal(metal="#D9DEE8", trim="#C99A3A", cloth="#3D5A9C", cloth2="#C8372E")
ASC = pal(metal="#CFE6F2", trim="#2B9FC4", cloth="#1F3D66", cloth2="#40E8FF")
TIERS = {
 "knight": [({"hair": "short", "chest": "vest", "legs": "trousers", "feet": "boots", "main": "sword", "head": "helm_plain"}, {"*": STEEL}, None),
            ({"chest": "plate", "legs": "greaves", "feet": "sabatons", "hands": "gauntlets", "main": "sword", "off": "shield", "head": "helm_plain"}, {"*": STEEL}, None),
            ({"chest": "plate", "legs": "greaves", "feet": "sabatons", "hands": "gauntlets", "main": "sword", "off": "shield", "head": "helm", "back": "cape"}, {"*": GOLDP}, None),
            ({"chest": "plate", "legs": "greaves", "feet": "sabatons", "hands": "gauntlets", "main": "lumen_blade", "off": "shield", "head": "helm", "back": "cape"}, {"*": ASC}, "#40E8FF")],
 "arcanist": [({"hair": "long", "chest": "robe", "feet": "boots", "main": "staff"}, {"*": pal(cloth="#8A3A2E", cloth2="#4A2A22", hair="#C2562E")}, None),
              ({"hair": "long", "chest": "robe", "feet": "boots", "main": "staff", "off": "tome", "hands": "gloves"}, {"*": pal(cloth="#2E6E8A", cloth2="#1C3E52", hair="#C2562E")}, None),
              ({"hair": "long", "chest": "robe", "feet": "boots", "main": "staff", "off": "tome", "head": "wizard_hat", "back": "cape"}, {"*": pal(cloth="#2C3E8C", cloth2="#E0B040", hair="#C2562E")}, None),
              ({"hair": "long", "chest": "robe", "feet": "boots", "main": "staff", "off": "tome", "head": "wizard_hat", "back": "cape"}, {"*": pal(cloth="#1F3D66", cloth2="#40E8FF", hair="#E8E2D8")}, "#40E8FF")],
 "tinker": [({"hair": "short", "chest": "vest", "legs": "trousers", "feet": "boots", "main": "pistol"}, {"*": pal(cloth="#3B5A8A", leather="#6E4A2E")}, None),
            ({"hair": "short", "chest": "coat", "legs": "trousers", "feet": "boots", "main": "pistol", "hands": "gloves", "head": "goggles"}, {"*": pal(cloth="#5A4632", cloth2="#2E241A")}, None),
            ({"chest": "plate", "legs": "greaves", "feet": "sabatons", "hands": "gauntlets", "main": "pistol", "off": "lantern", "head": "goggles", "hair": "short"}, {"*": pal(metal="#E0A030", trim="#6A4A1E", cloth="#3A3A44")}, None),
            ({"chest": "plate", "legs": "greaves", "feet": "sabatons", "hands": "gauntlets", "main": "pistol", "off": "lantern", "head": "goggles", "hair": "short", "back": "cape"}, {"*": ASC}, "#40E8FF")],
 "ranger": [({"hair": "short", "chest": "vest", "legs": "trousers", "feet": "boots", "main": "bow"}, {"*": pal(cloth="#4E6E34", leather="#6E4A2E")}, None),
            ({"hair": "short", "chest": "vest", "legs": "trousers", "feet": "boots", "main": "bow", "hands": "gloves", "head": "hood"}, {"*": pal(cloth="#3F6A2E", cloth2="#2A4420", leather="#5A3A22")}, None),
            ({"chest": "coat", "legs": "trousers", "feet": "boots", "main": "bow", "hands": "gloves", "head": "hood", "back": "cape"}, {"*": pal(cloth="#2E5A2A", cloth2="#C99A3A", leather="#4A3020")}, None),
            ({"chest": "coat", "legs": "trousers", "feet": "boots", "main": "bow", "hands": "gloves", "head": "hood", "back": "cape"}, {"*": pal(cloth="#1F4A3A", cloth2="#40E8FF", leather="#2E3A44")}, "#40E8FF")],
}
TIER_NAMES = {"knight": ["Squire", "Warden", "Lumen Paladin", "Ascended"], "arcanist": ["Hedge Caster", "Stormwright", "Starloom Magus", "Ascended"],
              "tinker": ["Scrap Apprentice", "Powder Gunsmith", "Engine Marshal", "Ascended"], "ranger": ["Wayfinder", "Thornwatch", "Greenveil Hunter", "Ascended"]}
REF16 = {"knight": ["knight_t1", "knight_t2", "knight_t3", "knight_t4"], "arcanist": ["arcanist_t1", "arcanist_t2", "arcanist_t3", "arcanist_t4"],
         "tinker": ["tinker_t1", "tinker_t2", "tinker_t3", "tinker_t4"], "ranger": ["ranger_t1", "ranger_t2", "ranger_t3", "ranger_t4"]}

if __name__ == "__main__":
    out = {"anchors": {k: v for k, v in A.items()}, "order": ORDER, "layers": [], "tiers": {}, "combos": []}
    os.makedirs(f"{R}/layers/body", exist_ok=True)
    for v in VIEWS + ["right"]:
        bm = body("left" if v == "right" else v); bm = mirror(bm) if v == "right" else bm
        render(bm, BASE_PAL).save(f"{R}/layers/body/base_{v}.png")
        for st in ("short", "long"):
            hm = hair("left" if v == "right" else v, st); hm = mirror(hm) if v == "right" else hm
            os.makedirs(f"{R}/layers/hair", exist_ok=True); render(hm, BASE_PAL).save(f"{R}/layers/hair/{st}_{v}.png")
        for slot, items in ITEMS.items():
            os.makedirs(f"{R}/layers/{slot}", exist_ok=True)
            for it in items:
                render(layer_mask(slot, it, v), BASE_PAL).save(f"{R}/layers/{slot}/{it}_{v}.png"); out["layers"].append(f"{slot}/{it}_{v}.png")
    os.makedirs(f"{R}/tiers", exist_ok=True); os.makedirs(f"{R}/combos", exist_ok=True)
    for cls, tiers in TIERS.items():
        out["tiers"][cls] = []
        for t, (lo, p, aura) in enumerate(tiers):
            for v in ("down", "left", "up", "right"):
                composite(lo, p, v, aura).save(f"{R}/tiers/{cls}_t{t+1}_{v}.png")
            out["tiers"][cls].append({"tier": t + 1, "name": TIER_NAMES[cls][t], "loadout": lo, "aura": aura, "ref16": REF16[cls][t]})
    # example combos for the Paper doll page
    combos = [("base", {"hair": "short"}, {"*": BASE_PAL}, None),
              ("mix_plate_hood_bow", {"chest": "plate", "legs": "greaves", "feet": "boots", "head": "hood", "main": "bow"}, {"*": STEEL}, None),
              ("mix_robe_shield_sword", {"hair": "long", "chest": "robe", "feet": "boots", "main": "sword", "off": "shield"}, {"*": pal(cloth="#6A3A8A", cloth2="#E0B040", hair="#2A1E16")}, None),
              ("mix_coat_goggles_staff", {"hair": "short", "chest": "coat", "legs": "trousers", "feet": "sabatons", "head": "goggles", "main": "staff", "off": "lantern"}, {"*": pal(cloth="#8A2E3A", cloth2="#2E1A1E")}, None),
              ("recolor_knight_t3_moss", TIERS["knight"][2][0], {"*": pal(metal="#B8C0A0", trim="#4E6E34", cloth="#3F5A2A", cloth2="#C99A3A")}, None),
              ("recolor_knight_t3_crimson", TIERS["knight"][2][0], {"*": pal(metal="#3A3A48", trim="#C8372E", cloth="#7A1E2A", cloth2="#E0B040")}, None)]
    for name, lo, p, aura in combos:
        composite(lo, p, "down", aura).save(f"{R}/combos/{name}.png"); out["combos"].append({"name": name, "loadout": lo})
    json.dump(out, open(f"{R}/doll.json", "w"), indent=1, default=str); print("ok", len(out["layers"]), "layers")
