"""Bake paper-doll animation sheets from one shared pose table.

Every layer is drawn on the same 64 x 64 grid. Idle, walk, and attack move the
same anchors (head, chest, hands, feet). Right-facing rows are the left rows
mirrored, so a runtime never flips layers on its own.

Sheet layout (8 columns x 12 rows, 512 x 768), matching docs/systems/paper-doll.md:

    rows 0-3   idle   down, left, up, right   4 frames
    rows 4-7   walk   down, left, up, right   8 frames
    rows 8-11  attack down, left, up, right   6 frames

Pixels are material indices, not final colors. Palette index = material * 5
+ step (0 outline, 1 deep shadow, 2 shadow, 3 base, 4 highlight). Index 0 is
empty. The PNG palette stores the index in the red channel so a loader can
recolor without guessing.

Usage (from the repo root, with art/requirements.txt installed):

    python art/doll/sheets.py

Rough spots left in this pass: right-facing rows are mirrors of left, the bowstring
is not pinched by the off glove (one shared hand table), and a few front-view
strike frames are stiffer than the side view.
"""
from __future__ import annotations

import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import doll  # noqa: E402
from doll import (  # noqa: E402
    ACCENT,
    CLOTH,
    CLOTH2,
    EYE,
    GEM,
    HAIR,
    HIDES_HAIR,
    LEATHER,
    METAL,
    N,
    ORDER,
    SKIN,
    TRIM,
    WHITE,
    WOOD,
    H,
    ell,
    grid,
    line,
    pal,
    ramp,
    rect,
)

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "hero")
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

DIRS = ("down", "left", "up", "right")
ANIMS = (("idle", 4, 6), ("walk", 8, 12), ("attack", 6, 16))
UPPER = ("head", "neck", "chest", "hip", "shoulder_m", "shoulder_o")

# Rest pose. Idle frame 0 is this pose. Spec anchors: head (32, 19),
# neck (32, 30), chest (32, 37), hip (32, 46), feet baseline y = 60,
# main/off grips as documented for down, up, and left.
BASE = {
    "down": {
        "head": (32, 19),
        "neck": (32, 30),
        "chest": (32, 37),
        "hip": (32, 46),
        "shoulder_m": (22, 33),
        "shoulder_o": (42, 33),
        "hand_m": (19, 45),
        "hand_o": (45, 45),
        "foot_m": (27, 60),
        "foot_o": (37, 60),
    },
    "up": {
        "head": (32, 19),
        "neck": (32, 30),
        "chest": (32, 37),
        "hip": (32, 46),
        "shoulder_m": (42, 33),
        "shoulder_o": (22, 33),
        "hand_m": (45, 45),
        "hand_o": (19, 45),
        "foot_m": (37, 60),
        "foot_o": (27, 60),
    },
    "left": {
        "head": (32, 19),
        "neck": (32, 30),
        "chest": (32, 37),
        "hip": (32, 46),
        "shoulder_m": (30, 33),
        "shoulder_o": (35, 34),
        "hand_m": (27, 44),
        "hand_o": (37, 43),
        "foot_m": (28, 60),
        "foot_o": (36, 60),
    },
}

# Walk: 8 frames, two steps. Feet lift off the baseline; the hip bobs.
BOB = (0, 0, -2, -1, 0, 0, -2, -1)
ARM = (5, 3, 0, -3, -5, -3, 0, 3)
LIFT_M = (0, 0, 2, 4, 5, 3, 1, 0)
LIFT_O = (5, 3, 1, 0, 0, 0, 2, 4)
STRIDE = (-6, -4, 0, 4, 6, 4, 0, -4)
LIFT_F = (0, 0, 1, 2, 1, 3, 4, 2)
LIFT_B = (1, 3, 4, 2, 0, 0, 1, 2)
CAPE_F = (2, 1, 0, -1, -2, -1, 0, 1)

# Attack: wind-up, wind-up, strike, strike, recover, recover.
# Hand offsets are from the rest grip. Side view forward is -x.
# Front slash stays on the main-hand side of the body so the blade is not
# the same color as the chest it crosses.
HAND_D = ((-4, -10), (-6, -16), (-2, -12), (-8, 2), (-4, 4), (0, 0))
HAND_OD = ((0, -2), (0, -3), (-1, -1), (-1, 0), (0, 0), (0, 0))
HAND_L = ((3, -4), (-2, -14), (-10, -10), (-12, -2), (-6, 2), (0, 0))
HAND_OL = ((1, -1), (2, -2), (1, 0), (0, 1), (0, 0), (0, 0))
SWORD_D = ((-4, -14), (-2, -16), (2, -14), (-8, 4), (-6, 6), (0, -14))
SWORD_L = ((2, -14), (-4, -14), (-14, -2), (-12, 2), (-8, 4), (-2, -12))
LUNGE_X = (1, 2, -1, -2, -1, 0)
LUNGE_Y = (0, -1, 0, 1, 0, 0)
BODY_DY = (-1, -2, -1, 1, 1, 0)
FOOT_L = (0, 0, -1, -3, -2, 0)
CAPE_AD = (1, 2, 0, -2, -1, 0)
CAPE_AL = (1, 2, 0, 3, 2, 0)
DRAW = (0.35, 0.75, 1.0, 0.0, 0.0, 0.1)
RECOIL = (0, 0, 2, 4, 2, 0)

# Up-facing strike: weapons move in front of the body so the swing reads.
# The coat stays on top of the torso. Hair is last so a long fall covers the coat.
UP_FRONT = ["body", "legs", "feet", "chest", "head", "arm_far", "sleeve_far", "hand_far", "main", "arm_near", "sleeve_near", "hand_near", "off", "back", "hair"]
ORDER_OVERRIDES = {"attack": {"up": {"1": UP_FRONT, "2": UP_FRONT, "3": UP_FRONT}}}

TWO_HAND = ("bow",)

NAMES = {
    "base": "Body",
    "short": "Short hair",
    "long": "Long hair",
    "cap": "Knit Cap",
    "mail_coif": "Mail Coif",
    "helm_plain": "Plain Helm",
    "tunic": "Homespun Tunic",
    "hauberk": "Mail Hauberk",
    "plate": "Plate Cuirass",
    "trousers": "Cloth Trousers",
    "mail_chausses": "Mail Chausses",
    "greaves": "Plate Greaves",
    "boots": "Leather Boots",
    "mail_boots": "Mail Boots",
    "sabatons": "Sabatons",
    "hand_wraps": "Hand Wraps",
    "gloves": "Leather Gloves",
    "gauntlets": "Plate Gauntlets",
    "cloak": "Travel Cloak",
    "quiver": "Quiver",
    "cape": "Cape",
    "sword": "Arming Sword",
    "bow": "Hunter Bow",
    "pistol": "Flintlock",
    "shield": "Heater Shield",
    "tome": "Tome",
    "lantern": "Waylamp Lantern",
    "hair_long_streak": "Long hair, silver streak",
    "veris_circlet": "Ferro Circlet",
    "veris_vest_plate": "Ocular Vest",
    "veris_greaves": "Ferro Greaves",
    "veris_heeled_boots": "Heeled Ferro Boots",
    "veris_gauntlets": "Ferro Gauntlets",
    "veris_longcoat": "Veris Longcoat",
    "ferro_blade": "Ferro Blade",
}


def put(g, x, y, m):
    if not m:
        return
    x = int(round(x))
    y = int(round(y))
    if 0 <= x < N and 0 <= y < N:
        g[y][x] = m


def stroke(g, x0, y0, x1, y1, m, w=1):
    line(g, int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1)), m, w)


def chain(g):
    """Break up metal fills so mail reads as links, not a solid plate."""
    for y in range(N):
        row = g[y]
        for x in range(N):
            if row[x] == METAL and ((x // 2) + (y // 2)) % 2 == 0:
                row[x] = TRIM


def limb(g, a, b, m, w, bend=0):
    ax, ay = a
    bx, by = b
    mx = (ax + bx) // 2 + int(bend)
    my = (ay + by) // 2
    stroke(g, ax, ay, mx, my, m, w)
    stroke(g, mx, my, bx, by, m, w)


def sleeve(g, shoulder, hand, t, m, w):
    end = (
        round(shoulder[0] + (hand[0] - shoulder[0]) * t),
        round(shoulder[1] + (hand[1] - shoulder[1]) * t),
    )
    stroke(g, shoulder[0], shoulder[1], end[0], end[1], m, w)


def torso(g, p, m, top_pad, bot_extra, width, side_width):
    top = p["neck"][1] + top_pad
    bot = p["hip"][1] + bot_extra
    if bot < top:
        return
    cx = p["chest"][0]
    w = side_width if p["view"] == "left" else width
    left = cx - w // 2
    rect(g, left, top, left + w - 1, bot, m)


def move(p, keys, dx, dy):
    for key in keys:
        x, y = p[key]
        p[key] = (x + dx, y + dy)


def make_pose(anim, view, frame):
    src = BASE[view]
    p = {key: src[key] for key in src}
    p.update(
        view=view,
        anim=anim,
        frame=frame,
        cape=0,
        arm=0,
        bend_m=0,
        bend_o=0,
        draw=0.0,
        release=False,
        recoil=0,
        flash=False,
    )
    if anim == "idle":
        breath = (0, -1, -1, 0)[frame]
        move(p, UPPER + ("hand_m", "hand_o"), 0, breath)
        p["cape"] = (0, 1, 0, -1)[frame]
        return p
    if anim == "walk":
        bob = BOB[frame]
        move(p, UPPER, 0, bob)
        arm = ARM[frame]
        p["arm"] = arm
        if view == "left":
            move(p, ("hand_m",), -STRIDE[frame] // 2, bob)
            move(p, ("hand_o",), STRIDE[frame] // 3, bob)
            p["foot_m"] = (p["foot_m"][0] + STRIDE[frame], p["foot_m"][1] - LIFT_F[frame])
            p["foot_o"] = (p["foot_o"][0] - STRIDE[frame], p["foot_o"][1] - LIFT_B[frame])
            p["bend_m"] = -max(0, LIFT_F[frame] // 2)
            p["bend_o"] = max(0, LIFT_B[frame] // 2)
            # Stride is negative when the front foot is forward, so the cape lags +x.
            p["cape"] = -STRIDE[frame] // 2
        else:
            move(p, ("hand_m",), 0, bob + arm)
            move(p, ("hand_o",), 0, bob - arm)
            sign = -1 if view == "down" else 1
            lift_m, lift_o = LIFT_M[frame], LIFT_O[frame]
            p["foot_m"] = (p["foot_m"][0] + sign * (1 if lift_m > 2 else 0), p["foot_m"][1] - lift_m)
            p["foot_o"] = (p["foot_o"][0] - sign * (1 if lift_o > 2 else 0), p["foot_o"][1] - lift_o)
            p["bend_m"] = sign * (lift_m // 2)
            p["bend_o"] = -sign * (lift_o // 2)
            p["cape"] = CAPE_F[frame] if view == "down" else -CAPE_F[frame]
        return p
    # attack
    if view == "left":
        move(p, ("head", "neck", "chest", "shoulder_m", "shoulder_o"), LUNGE_X[frame], LUNGE_Y[frame])
        move(p, ("hip",), LUNGE_X[frame] // 2, 0)
        hx, hy = HAND_L[frame]
        ox, oy = HAND_OL[frame]
        move(p, ("hand_m",), hx, hy)
        move(p, ("hand_o",), ox, oy)
        p["foot_m"] = (p["foot_m"][0] + FOOT_L[frame], p["foot_m"][1])
        p["bend_m"] = -2 if frame in (2, 3) else 0
        p["cape"] = CAPE_AL[frame]
    else:
        sign = 1 if view == "down" else -1
        move(p, UPPER, 0, BODY_DY[frame])
        hx, hy = HAND_D[frame]
        ox, oy = HAND_OD[frame]
        move(p, ("hand_m",), sign * hx, hy)
        move(p, ("hand_o",), sign * ox, oy)
        p["cape"] = sign * CAPE_AD[frame]
    p["draw"] = DRAW[frame]
    p["release"] = frame in (3, 4)
    p["recoil"] = RECOIL[frame]
    p["flash"] = frame in (2, 3)
    return p


def aim_vec(view):
    if view == "left":
        return (-12, 1)
    if view == "up":
        return (0, -12)
    return (1, 12)


def sword_tip(p):
    view, anim, frame = p["view"], p["anim"], p["frame"]
    if anim == "attack":
        dx, dy = SWORD_L[frame] if view == "left" else SWORD_D[frame]
        if view == "up":
            dx = -dx
        return dx, dy
    lag = p["arm"]
    if view == "left":
        return (-4 + lag // 2, -16)
    if view == "up":
        return (-lag // 2, -16)
    return (lag // 2, -16)


def leg_pairs(p):
    hip = p["hip"]
    if p["view"] == "left":
        pairs = [
            ((hip[0] + 2, hip[1]), p["foot_o"], p["bend_o"], 4),
            ((hip[0] - 1, hip[1]), p["foot_m"], p["bend_m"], 5),
        ]
        pairs.sort(key=lambda item: -item[1][0])
        return pairs
    return [
        ((hip[0] - 5, hip[1]), p["foot_m"], p["bend_m"], 5),
        ((hip[0] + 5, hip[1]), p["foot_o"], p["bend_o"], 5),
    ]


def draw_legs(g, p, m, y0_pad, y1_pad, extra_w, band=False):
    for hip_pt, foot, bend, width in leg_pairs(p):
        start = (hip_pt[0], hip_pt[1] + y0_pad)
        end = (foot[0], foot[1] - y1_pad)
        limb(g, start, end, m, width + extra_w, bend)
        if band:
            mx = (start[0] + end[0]) // 2 + int(bend)
            my = (start[1] + end[1]) // 2
            rect(g, mx - 3, my, mx + 3, my + 1, TRIM)


def draw_feet(g, p, kind):
    view = p["view"]
    feet = sorted((p["foot_m"], p["foot_o"]), key=lambda foot: foot[1])
    for fx, fy in feet:
        if kind == "wraps":
            rect(g, fx - 3, fy - 3, fx + 3, fy, LEATHER)
        elif kind == "boots":
            rect(g, fx - 4, fy - 7, fx + 4, fy, LEATHER)
            rect(g, fx - 4, fy - 1, fx + 4, fy, TRIM)
            if view == "left":
                rect(g, fx - 7, fy - 3, fx - 4, fy, LEATHER)
        elif kind == "mail_boots":
            rect(g, fx - 4, fy - 9, fx + 4, fy, METAL)
            if view == "left":
                rect(g, fx - 7, fy - 3, fx - 4, fy, METAL)
        else:
            rect(g, fx - 4, fy - 6, fx + 4, fy, METAL)
            rect(g, fx - 3, fy - 4, fx + 3, fy - 3, TRIM)
            if view == "left":
                rect(g, fx - 8, fy - 3, fx - 3, fy, METAL)
            elif fy + 1 < N:
                rect(g, fx - 2, fy + 1, fx + 2, fy + 1, METAL)
        put(g, fx, fy, LEATHER if kind in ("wraps", "boots") else METAL)
    if kind == "mail_boots":
        chain(g)
        for fx, fy in feet:
            rect(g, fx - 4, fy - 1, fx + 4, fy, LEATHER)
            put(g, fx, fy, LEATHER)


def paint_one_hand(g, p, kind, side):
    _shoulder, (hx, hy) = arm_points(p, side)
    if kind == "wraps":
        rect(g, hx - 3, hy - 1, hx + 3, hy + 1, CLOTH)
        rect(g, hx - 2, hy - 4, hx + 2, hy - 3, CLOTH2)
        put(g, hx, hy, CLOTH)
    elif kind == "gloves":
        ell(g, hx, hy, 4, 3.4, LEATHER)
        rect(g, hx - 2, hy - 5, hx + 2, hy - 3, TRIM)
        put(g, hx, hy, LEATHER)
    else:
        ell(g, hx, hy, 4.2, 3.6, METAL)
        rect(g, hx - 3, hy - 6, hx + 3, hy - 3, TRIM)
        put(g, hx - 1, hy - 1, TRIM)
        put(g, hx, hy, METAL)


def hair_tail(g, x0, x1, y0, y1, skew, mat=HAIR):
    span = max(1, y1 - y0)
    for y in range(y0, y1):
        shift = round(skew * (y - y0) / span)
        rect(g, x0 + shift, y, x1 + shift, y, mat)


def arm_points(p, side):
    """Far arm is the character's right hand (main). Near arm is the left hand (off)."""
    if side == "far":
        return p["shoulder_m"], p["hand_m"]
    return p["shoulder_o"], p["hand_o"]


def paint_body(g, p):
    view = p["view"]
    for hip_pt, foot, bend, width in leg_pairs(p):
        limb(g, hip_pt, (foot[0], foot[1] - 2), SKIN, width, bend)
    torso(g, p, CLOTH, 1, 1, 18, 12)
    draw_feet(g, p, "wraps")
    neck = p["neck"]
    rect(g, neck[0] - 3, neck[1] - 1, neck[0] + 3, neck[1] + 2, SKIN)
    hx, hy = p["head"]
    if view == "left":
        ell(g, hx, hy, 11, 11, SKIN)
        rect(g, hx - 8, hy, hx - 7, hy + 3, EYE)
        put(g, hx - 8, hy, WHITE)
        rect(g, hx - 12, hy + 2, hx - 10, hy + 4, SKIN)
    elif view == "down":
        ell(g, hx, hy, 12, 11, SKIN)
        rect(g, hx - 6, hy, hx - 5, hy + 3, EYE)
        rect(g, hx + 5, hy, hx + 6, hy + 3, EYE)
        put(g, hx - 6, hy, WHITE)
        put(g, hx + 5, hy, WHITE)
        rect(g, hx - 1, hy + 6, hx + 1, hy + 6, CLOTH2)
    else:
        ell(g, hx, hy, 12, 11, SKIN)
    put(g, hx, hy, SKIN)


def paint_hair(g, p, style):
    hx, hy = p["head"]
    view = p["view"]
    skew = p["cape"]
    if view == "down":
        ell(g, hx, hy - 4, 12.5, 8, HAIR, y_max=hy - 2)
        rect(g, hx - 12, hy - 5, hx - 10, hy + 2, HAIR)
        rect(g, hx + 10, hy - 5, hx + 12, hy + 2, HAIR)
        if style == "long":
            hair_tail(g, hx - 13, hx - 10, hy - 2, hy + 12, skew)
            hair_tail(g, hx + 10, hx + 13, hy - 2, hy + 12, skew)
    elif view == "up":
        ell(g, hx, hy, 12.5, 11.5, HAIR)
        if style == "long":
            hair_tail(g, hx - 10, hx + 10, hy + 5, hy + 16, skew)
    else:
        ell(g, hx + 2, hy - 3, 10, 8, HAIR, y_max=hy)
        rect(g, hx + 3, hy - 4, hx + 11, hy + 5, HAIR)
        if style == "long":
            hair_tail(g, hx + 4, hx + 11, hy + 2, hy + 16, skew)
    put(g, hx, hy - 6, HAIR)


def paint_cap(g, p):
    hx, hy = p["head"]
    view = p["view"]
    if view == "left":
        ell(g, hx + 1, hy - 4, 11, 7, CLOTH, y_max=hy - 2)
        rect(g, hx - 10, hy - 3, hx + 6, hy - 2, CLOTH2)
    elif view == "up":
        ell(g, hx, hy - 2, 12, 9, CLOTH)
        rect(g, hx - 8, hy - 6, hx + 8, hy - 5, CLOTH2)
    else:
        ell(g, hx, hy - 5, 12, 8, CLOTH, y_max=hy - 2)
        rect(g, hx - 8, hy - 7, hx + 8, hy - 6, CLOTH2)
        rect(g, hx - 12, hy - 3, hx + 12, hy - 2, CLOTH)
    put(g, hx, hy - 7, CLOTH)


def paint_coif(g, p):
    hx, hy = p["head"]
    neck = p["neck"]
    view = p["view"]
    if view == "up":
        ell(g, hx, hy, 13, 12, METAL)
        rect(g, neck[0] - 8, neck[1] - 2, neck[0] + 8, neck[1] + 4, METAL)
    elif view == "left":
        ell(g, hx + 1, hy, 12, 12, METAL)
        rect(g, hx - 1, hy + 6, hx + 8, neck[1] + 3, METAL)
        chain(g)
        doll.clear(g, hx - 14, hy - 5, hx - 1, hy + 7)
    else:
        ell(g, hx, hy, 13, 12, METAL)
        rect(g, hx - 8, hy + 7, hx + 8, neck[1] + 3, METAL)
        chain(g)
        doll.clear(g, hx - 9, hy - 4, hx + 9, hy + 8)
    if view == "up":
        chain(g)
    put(g, hx, hy - 8, METAL)


def paint_helm(g, p):
    hx, hy = p["head"]
    view = p["view"]
    if view == "up":
        ell(g, hx, hy, 13, 12, METAL)
        rect(g, hx - 2, hy - 14, hx + 2, hy - 6, TRIM)
    elif view == "left":
        ell(g, hx + 1, hy - 1, 12, 11, METAL, y_max=hy + 1)
        rect(g, hx - 1, hy + 1, hx + 7, hy + 6, METAL)
        doll.clear(g, hx - 14, hy - 1, hx - 4, hy + 6)
        rect(g, hx - 8, hy - 2, hx + 6, hy - 1, TRIM)
        rect(g, hx - 10, hy, hx - 8, hy + 3, METAL)
    else:
        ell(g, hx, hy - 1, 13, 11, METAL, y_max=hy)
        rect(g, hx - 13, hy + 1, hx - 7, hy + 7, METAL)
        rect(g, hx + 7, hy + 1, hx + 13, hy + 7, METAL)
        rect(g, hx - 12, hy - 1, hx + 12, hy, TRIM)
        rect(g, hx - 5, hy + 8, hx + 5, hy + 10, METAL)
    put(g, hx, hy - 8, METAL)


def paint_arm(g, p, side):
    shoulder, hand = arm_points(p, side)
    stroke(g, shoulder[0], shoulder[1], hand[0], hand[1], SKIN, 4 if p["view"] == "left" else 5)
    ell(g, hand[0], hand[1], 3.1, 3.1, SKIN)
    put(g, hand[0], hand[1], SKIN)


def paint_tunic(g, p):
    torso(g, p, CLOTH, 2, 2, 20, 13)
    hip = p["hip"]
    rect(g, hip[0] - (6 if p["view"] == "left" else 8), hip[1] + 1, hip[0] + (5 if p["view"] == "left" else 8), hip[1] + 2, LEATHER)
    if p["view"] == "down":
        neck = p["neck"]
        doll.clear(g, neck[0] - 2, neck[1], neck[0] + 2, neck[1] + 3)
    put(g, p["chest"][0], p["chest"][1], CLOTH)


def paint_sleeve(g, p, kind, side):
    shoulder, hand = arm_points(p, side)
    if kind == "tunic":
        sleeve(g, shoulder, hand, 0.5, CLOTH, 5)
    elif kind == "hauberk":
        sleeve(g, shoulder, hand, 0.82, METAL, 5)
        chain(g)
    else:
        ell(g, shoulder[0], shoulder[1], 5.5, 4.5, METAL)
        sleeve(g, shoulder, hand, 0.38, METAL, 5)
    put(g, shoulder[0], shoulder[1], METAL if kind != "tunic" else CLOTH)


def paint_hauberk(g, p):
    torso(g, p, METAL, 0, 8, 20, 13)
    chain(g)
    hip = p["hip"]
    y = hip[1] + 7
    half = 6 if p["view"] == "left" else 9
    rect(g, hip[0] - half, y, hip[0] + half, y + 1, TRIM)
    put(g, p["chest"][0], p["chest"][1], METAL)


def paint_plate(g, p):
    torso(g, p, METAL, 1, 2, 20, 14)
    if p["view"] != "left":
        rect(g, p["chest"][0] - 1, p["neck"][1] + 2, p["chest"][0] + 1, p["hip"][1], TRIM)
        rect(g, p["chest"][0] - 6, p["chest"][1] + 1, p["chest"][0] + 6, p["chest"][1] + 1, TRIM)
    else:
        rect(g, p["chest"][0] + 2, p["neck"][1] + 2, p["chest"][0] + 3, p["hip"][1], TRIM)
    hip = p["hip"]
    if p["view"] == "left":
        rect(g, hip[0] - 6, hip[1], hip[0] + 4, hip[1] + 4, METAL)
    else:
        rect(g, hip[0] - 10, hip[1], hip[0] - 3, hip[1] + 4, METAL)
        rect(g, hip[0] + 3, hip[1], hip[0] + 10, hip[1] + 4, METAL)
    rect(g, hip[0] - 8, hip[1] + 1, hip[0] + 8, hip[1] + 2, TRIM)
    put(g, p["chest"][0], p["chest"][1], METAL)


def paint_trousers(g, p):
    draw_legs(g, p, CLOTH, 0, 4, 1)
    put(g, p["hip"][0], p["hip"][1] + 2, CLOTH)


def paint_chausses(g, p):
    for hip_pt, foot, bend, width in leg_pairs(p):
        mid = ((hip_pt[0] + foot[0]) // 2 + int(bend), (hip_pt[1] + foot[1]) // 2)
        limb(g, hip_pt, mid, METAL, width + 1, bend)
        rect(g, mid[0] - 3, mid[1], mid[0] + 3, mid[1] + 1, TRIM)
    chain(g)
    put(g, p["hip"][0], p["hip"][1] + 2, METAL)


def paint_greaves(g, p):
    draw_legs(g, p, METAL, 1, 2, 1, band=True)
    put(g, p["hip"][0], p["hip"][1] + 3, METAL)


def paint_boots(g, p):
    draw_feet(g, p, "boots")


def paint_mail_boots(g, p):
    draw_feet(g, p, "mail_boots")


def paint_sabatons(g, p):
    draw_feet(g, p, "sabatons")


def paint_wraps(g, p, side):
    paint_one_hand(g, p, "wraps", side)


def paint_gloves(g, p, side):
    paint_one_hand(g, p, "gloves", side)


def paint_gauntlets(g, p, side):
    paint_one_hand(g, p, "gauntlets", side)


def paint_drape(g, p, length, flare, sway_scale, mat):
    top = p["neck"][1] - 1
    bot = min(N - 2, top + length)
    cx = p["chest"][0]
    sway = p["cape"] * sway_scale
    view = p["view"]
    span = max(1, bot - top)
    if view == "left":
        for y in range(top, bot):
            t = (y - top) / span
            width = 3 + int(t * flare)
            shift = round(sway * t)
            x0 = cx + 5 + shift
            rect(g, x0, y, x0 + width, y, mat)
        rect(g, cx + 4, top, cx + 9, top + 2, CLOTH2)
    else:
        half0 = 10 if view == "up" else 7
        for y in range(top, bot):
            t = (y - top) / span
            half = half0 + int(t * flare)
            shift = round(sway * t)
            rect(g, cx - half + shift, y, cx + half + shift, y, mat)
        rect(g, cx - 5, top, cx + 5, top + 2, CLOTH2)
        if view == "up":
            rect(g, cx - 2, top + 1, cx + 2, top + 3, TRIM)
    put(g, cx, top + 1, mat)


def paint_cape(g, p):
    paint_drape(g, p, 22, 6, 1, CLOTH)


def paint_cloak(g, p):
    paint_drape(g, p, 26, 8, 2, CLOTH)


def paint_quiver(g, p):
    chest = p["chest"]
    neck = p["neck"]
    shift = round(p["cape"] * 0.6)
    view = p["view"]
    if view == "left":
        x = chest[0] + 7 + shift
        rect(g, x, neck[1] - 1, x + 4, chest[1] + 8, LEATHER)
        for i, y in enumerate(range(neck[1] - 9, neck[1] - 1)):
            put(g, x + 1 + (i % 2), y, WHITE if y < neck[1] - 6 else WOOD)
    elif view == "up":
        x = chest[0] + 8 + shift
        rect(g, x - 2, neck[1] + 1, x + 4, chest[1] + 10, LEATHER)
        rect(g, x - 1, neck[1] - 8, x + 3, neck[1], WOOD)
        rect(g, x - 1, neck[1] - 11, x + 3, neck[1] - 8, WHITE)
    else:
        x = chest[0] + 14 + shift
        rect(g, x, neck[1] + 2, x + 4, chest[1] + 8, LEATHER)
        for i, y in enumerate(range(neck[1] - 12, neck[1] + 1)):
            put(g, x + (i % 3) - 1, y, WHITE if y < neck[1] - 5 else WOOD)
    # Strap shares the neck anchor with capes, so the quiver cannot drift off the shoulders.
    stroke(g, neck[0], neck[1], x + 1, neck[1] + 6, LEATHER, 2)
    put(g, neck[0], neck[1], LEATHER)


def paint_sword(g, p):
    x, y = p["hand_m"]
    dx, dy = sword_tip(p)
    # At rest the blade sits just outside the arm, or it vanishes into mail and plate.
    if p["anim"] == "attack":
        x0, y0 = x, y
    elif p["view"] == "down":
        x0, y0 = x - 4, y
    elif p["view"] == "up":
        x0, y0 = x + 4, y
    else:
        x0, y0 = x - 6, y - 1
    stroke(g, x0, y0, x0 + dx, y0 + dy, METAL, 3)
    mag = max((dx * dx + dy * dy) ** 0.5, 1)
    px, py = -dy / mag, dx / mag
    gx = x + dx * 0.16
    gy = y + dy * 0.16
    stroke(g, gx - px * 4, gy - py * 3, gx + px * 4, gy + py * 3, TRIM, 2)
    stroke(g, x, y, x - dx * 0.18, y - dy * 0.18, LEATHER, 2)
    put(g, x0 + dx, y0 + dy, METAL)
    put(g, x, y, LEATHER)


def paint_bow(g, p):
    x, y = p["hand_m"]
    view = p["view"]
    # Tips sit back from the belly. Resting string is already off the wood so it is not a staff.
    pull = 4 + int(round(p["draw"] * 6))
    if view == "up":
        sign = -1
    else:
        sign = 1
    top, bot = y - 14, y + 8
    for yy in range(top, bot + 1):
        t = (yy - y) / 14
        curve = round((t * t) * 7)
        bx = x + sign * curve
        put(g, bx, yy, WOOD)
        put(g, bx + sign, yy, WOOD)
    tip_a = (x + sign * 7, top)
    tip_b = (x + sign * 7, bot)
    nock = (x + sign * (7 + pull), y)
    stroke(g, tip_a[0], tip_a[1], nock[0], nock[1], WHITE, 1)
    stroke(g, nock[0], nock[1], tip_b[0], tip_b[1], WHITE, 1)
    ux, uy = aim_vec(view)
    mag = max((ux * ux + uy * uy) ** 0.5, 1)
    ux, uy = ux / mag, uy / mag
    if p["release"]:
        length = 16 if p["frame"] == 3 else 7
        start = (x + ux * 6, y + uy * 6)
        shaft = (start[0] + ux * length, start[1] + uy * length)
        stroke(g, start[0], start[1], shaft[0], shaft[1], WOOD, 1)
        put(g, shaft[0], shaft[1], TRIM)
        put(g, start[0], start[1], WHITE)
    elif p["anim"] == "attack" and p["draw"] > 0.2:
        start = (nock[0], nock[1])
        shaft = (start[0] + ux * 12, start[1] + uy * 12)
        stroke(g, start[0], start[1], shaft[0], shaft[1], WOOD, 1)
        put(g, shaft[0], shaft[1], TRIM)
        put(g, start[0], start[1], WHITE)
    put(g, x, y, WOOD)


def paint_pistol(g, p):
    """Flintlock silhouette: thick barrel, dropped wood grip, small cock. One cyan muzzle pixel."""
    x, y = p["hand_m"]
    view = p["view"]
    recoil = p["recoil"]
    if view == "left":
        muzzle = x - (12 - recoil)
        rect(g, muzzle, y - 2, x - 1, y + 1, METAL)
        rect(g, x - 1, y, x + 3, y + 6, WOOD)
        rect(g, x - 3, y - 4, x - 1, y, TRIM)
        put(g, muzzle, y - 1, ACCENT)
        flash_at = (muzzle - 2, y - 1)
    elif view == "up":
        muzzle_y = y - (11 - recoil)
        rect(g, x - 1, muzzle_y, x + 2, y - 1, METAL)
        rect(g, x - 5, y, x, y + 5, WOOD)
        rect(g, x + 1, y - 3, x + 4, y, TRIM)
        put(g, x, muzzle_y, ACCENT)
        flash_at = (x, muzzle_y - 2)
    else:
        # Facing the camera: hold the gun out beside the body, barrel toward the bottom of the frame.
        barrel_x = x - 2
        muzzle_y = y + (12 - recoil)
        rect(g, barrel_x, y + 1, barrel_x + 1, muzzle_y, METAL)
        rect(g, barrel_x - 4, y + 2, barrel_x - 1, y + 7, WOOD)
        rect(g, barrel_x, y - 2, barrel_x + 2, y + 1, TRIM)
        put(g, barrel_x, muzzle_y, ACCENT)
        flash_at = (barrel_x, muzzle_y + 2)
    if p["flash"]:
        fx, fy = flash_at
        for ox, oy in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1), (2, 0)):
            put(g, fx + ox, fy + oy, WHITE)
        put(g, fx + 1, fy - 1, ACCENT)
    put(g, x, y, WOOD)


def paint_shield(g, p):
    x, y = p["hand_o"]
    view = p["view"]
    if view == "left":
        rect(g, x - 1, y - 12, x + 5, y + 8, METAL)
        rect(g, x + 1, y - 10, x + 3, y + 6, CLOTH2)
    elif view == "up":
        rect(g, x - 7, y - 12, x + 7, y + 2, LEATHER)
        for i in range(6):
            rect(g, x - 5 + i, y + 2 + i, x + 5 - i, y + 2 + i, LEATHER)
        rect(g, x - 7, y - 12, x + 7, y - 11, TRIM)
    else:
        rect(g, x - 7, y - 12, x + 7, y + 1, METAL)
        for i in range(6):
            rect(g, x - 5 + i, y + 1 + i, x + 5 - i, y + 1 + i, METAL)
        rect(g, x - 7, y - 12, x + 7, y - 11, TRIM)
        rect(g, x - 1, y - 9, x + 1, y + 4, CLOTH2)
        rect(g, x - 4, y - 4, x + 4, y - 2, CLOTH2)
    put(g, x, y, METAL if view != "up" else LEATHER)


def paint_tome(g, p):
    x, y = p["hand_o"]
    view = p["view"]
    opened = 2 if p["anim"] == "attack" and p["frame"] in (1, 2, 3) else 0
    if view == "up":
        rect(g, x - 4, y - 6, x + 4, y + 3, CLOTH2)
    elif view == "left":
        rect(g, x - 2, y - 6, x + 3 + opened, y + 4, CLOTH2)
        rect(g, x - 1, y - 5, x + 2 + opened, y + 3, WHITE)
        rect(g, x, y - 1, x + 2, y - 1, ACCENT)
    else:
        rect(g, x - 5 - opened, y - 6, x + 5 + opened, y + 3, CLOTH2)
        rect(g, x - 4 - opened, y - 5, x + 4 + opened, y + 2, WHITE)
        rect(g, x - 1, y - 5, x + 1, y + 2, CLOTH2)
        rect(g, x - 4, y - 1, x + 4, y, ACCENT)
    put(g, x, y, CLOTH2)


def paint_lantern(g, p):
    x, y = p["hand_o"]
    swing = p["cape"]
    stroke(g, x, y, x, y + 3, TRIM, 1)
    cx = x + swing
    rect(g, cx - 3, y + 3, cx + 3, y + 12, TRIM)
    rect(g, cx - 2, y + 4, cx + 2, y + 11, ACCENT)
    rect(g, cx - 3, y + 3, cx + 3, y + 4, METAL)
    put(g, x, y, TRIM)


def paint_hair_streak(g, p):
    """Long black hair with a silver-gray streak at the front left."""
    paint_hair(g, p, "long")
    hx, hy = p["head"]
    skew = p["cape"]
    view = p["view"]
    if view == "down":
        hair_tail(g, hx - 13, hx - 11, hy - 5, hy + 13, skew, METAL)
        put(g, hx - 12, hy + 2, WHITE)
    elif view == "up":
        hair_tail(g, hx - 7, hx - 4, hy + 6, hy + 16, skew, METAL)
        put(g, hx - 5, hy + 10, WHITE)
    else:
        hair_tail(g, hx + 3, hx + 5, hy - 2, hy + 14, skew, METAL)
        put(g, hx + 4, hy + 4, WHITE)
    put(g, hx, hy - 6, HAIR)


def paint_circlet(g, p):
    hx, hy = p["head"]
    view = p["view"]
    y = hy - 5
    if view == "left":
        rect(g, hx - 5, y, hx + 4, y + 1, METAL)
        put(g, hx - 5, y, GEM)
        put(g, hx - 4, y, ACCENT)
    elif view == "up":
        rect(g, hx - 6, y, hx + 6, y + 1, METAL)
        put(g, hx, y, GEM)
    else:
        rect(g, hx - 7, y, hx + 7, y + 1, METAL)
        put(g, hx, y, GEM)
        put(g, hx, y - 1, ACCENT)
    put(g, hx, hy - 7, METAL)


def ocular(g, x, y):
    """Silver ring, violet core, one pale emissive pixel."""
    rect(g, x - 2, y - 2, x + 2, y + 2, METAL)
    put(g, x - 1, y, ACCENT)
    put(g, x + 1, y, ACCENT)
    put(g, x, y - 1, ACCENT)
    put(g, x, y + 1, ACCENT)
    put(g, x, y, WHITE)


def paint_veris_vest(g, p):
    chest = p["chest"]
    neck = p["neck"]
    hip = p["hip"]
    view = p["view"]
    cx, cy = chest
    if view == "up":
        rect(g, cx - 5, neck[1], cx + 5, cy + 2, TRIM)
    elif view == "left":
        rect(g, cx - 5, neck[1] + 1, cx + 1, hip[1] + 1, TRIM)
        rect(g, cx - 4, cy - 3, cx, cy + 3, METAL)
        rect(g, cx - 4, cy - 3, cx, cy - 3, WHITE)
        ocular(g, cx - 2, cy)
        put(g, cx - 4, cy + 2, GEM)
    else:
        rect(g, cx - 6, neck[1] + 1, cx + 6, hip[1] + 1, TRIM)
        rect(g, cx - 4, cy - 4, cx + 4, cy + 4, METAL)
        rect(g, cx - 4, cy - 4, cx + 4, cy - 4, WHITE)
        ocular(g, cx, cy)
        put(g, cx - 3, cy + 3, GEM)
        put(g, cx + 3, cy + 3, GEM)
    put(g, cx, cy, METAL)


def paint_veris_sleeve(g, p, side):
    shoulder, hand = arm_points(p, side)
    sx, sy = shoulder
    ell(g, sx, sy, 6, 4.4, METAL)
    out = -1 if sx < p["chest"][0] else 1
    put(g, sx + out * 3, sy - 5, METAL)
    put(g, sx + out * 2, sy - 4, METAL)
    put(g, sx + out, sy - 3, TRIM)
    sleeve(g, shoulder, hand, 0.62, METAL, 4)
    put(g, sx, sy - 1, GEM)
    put(g, sx + out, sy, ACCENT)
    put(g, sx, sy, METAL)


def coat_tails(g, specs, sway):
    """Two or three chunky hem points. The tips swing farther than the roots."""
    for i, (x, y0, y1) in enumerate(specs):
        span = max(1, y1 - y0)
        gain = 1.6 + i * 0.25
        for y in range(y0, y1 + 1):
            shift = round(sway * gain * (y - y0) / span)
            rect(g, x + shift, y, x + 2 + shift, y, CLOTH)
            if y % 4 == 0:
                put(g, x + shift, y, CLOTH2)
        tip = round(sway * gain)
        put(g, x + 1 + tip, y1, METAL)


def paint_veris_coat(g, p):
    neck = p["neck"]
    chest = p["chest"]
    sway = p["cape"]
    view = p["view"]
    cx = chest[0]
    top = neck[1] - 1
    if view == "left":
        rect(g, cx + 4, top, cx + 10, 51, CLOTH)
        rect(g, cx + 9, top + 2, cx + 10, 50, CLOTH2)
        for y in range(top + 3, 50, 4):
            put(g, cx + 10, y, METAL)
        rect(g, neck[0] + 4, neck[1] - 2, neck[0] + 8, neck[1] + 2, CLOTH)
        put(g, neck[0] + 8, neck[1] - 2, METAL)
        coat_tails(g, [(cx + 4, 49, 58), (cx + 7, 49, 61), (cx + 10, 49, 56)], sway)
        put(g, neck[0] + 6, neck[1], CLOTH)
    elif view == "up":
        rect(g, cx - 9, top - 1, cx + 9, 51, CLOTH)
        rect(g, cx - 9, top, cx - 8, 50, CLOTH2)
        rect(g, cx + 8, top, cx + 9, 50, CLOTH2)
        for y in range(top + 3, 50, 4):
            put(g, cx - 9, y, METAL)
            put(g, cx + 9, y, METAL)
        rect(g, cx - 5, neck[1] - 4, cx + 5, neck[1] + 1, CLOTH)
        rect(g, cx - 5, neck[1] - 4, cx + 5, neck[1] - 3, METAL)
        ocular(g, cx, chest[1] + 2)
        for i, y in enumerate(range(chest[1] + 8, chest[1] + 16)):
            put(g, cx + 6 + (i % 2), y, METAL)
            put(g, cx + 7 + (i % 2), y, TRIM)
        coat_tails(g, [(cx - 7, 49, 59), (cx - 1, 49, 61), (cx + 5, 49, 57)], sway)
        put(g, neck[0], neck[1], CLOTH)
    else:
        rect(g, cx - 12, top, cx - 9, 51, CLOTH)
        rect(g, cx + 9, top, cx + 12, 51, CLOTH)
        rect(g, cx - 12, top + 1, cx - 12, 50, CLOTH2)
        rect(g, cx + 12, top + 1, cx + 12, 50, CLOTH2)
        for y in range(top + 3, 50, 4):
            put(g, cx - 11, y, METAL)
            put(g, cx + 11, y, METAL)
        rect(g, neck[0] - 8, neck[1] - 4, neck[0] - 6, neck[1] + 1, CLOTH)
        rect(g, neck[0] + 6, neck[1] - 4, neck[0] + 8, neck[1] + 1, CLOTH)
        put(g, neck[0] - 8, neck[1] - 4, METAL)
        put(g, neck[0] + 8, neck[1] - 4, METAL)
        coat_tails(g, [(cx - 11, 49, 59), (cx - 1, 50, 57), (cx + 8, 49, 61)], sway)
        put(g, neck[0], neck[1], CLOTH)


def paint_veris_greaves(g, p):
    paint_greaves(g, p)
    hip = p["hip"]
    hx, hy = hip
    if p["view"] == "left":
        rect(g, hx - 4, hy - 1, hx + 2, hy + 5, METAL)
        put(g, hx - 2, hy + 1, GEM)
    else:
        rect(g, hx - 8, hy - 1, hx - 2, hy + 5, METAL)
        rect(g, hx + 2, hy - 1, hx + 8, hy + 5, METAL)
        put(g, hx - 5, hy + 1, GEM)
        put(g, hx + 5, hy + 1, GEM)
    put(g, hx, hy + 3, METAL)


def paint_veris_boots(g, p):
    view = p["view"]
    for fx, fy in (p["foot_m"], p["foot_o"]):
        rect(g, fx - 3, fy - 11, fx + 3, fy - 2, CLOTH)
        rim = fx + 3 if view == "left" else fx - 3
        rect(g, rim, fy - 10, rim, fy - 3, CLOTH2)
        rect(g, fx - 2, fy - 9, fx + 2, fy - 5, METAL)
        put(g, fx, fy - 7, GEM)
        rect(g, fx - 4, fy - 2, fx + 4, fy, CLOTH)
        if view == "left":
            rect(g, fx + 3, fy - 5, fx + 5, fy, CLOTH)
            put(g, fx + 4, fy - 2, METAL)
        else:
            rect(g, fx - 1, fy - 1, fx + 1, fy - 1, METAL)
        put(g, fx, fy, CLOTH)


def paint_veris_gauntlet(g, p, side):
    shoulder, hand = arm_points(p, side)
    hx, hy = hand
    sx, sy = shoulder
    # Bracer covers the forearm so a thrust does not show bare skin.
    stroke(g, hx, hy, hx + (sx - hx) * 0.5, hy + (sy - hy) * 0.5, METAL, 4)
    ell(g, hx, hy, 4.2, 3.6, METAL)
    rect(g, hx - 3, hy - 5, hx + 3, hy - 3, TRIM)
    rect(g, hx - 2, hy - 4, hx + 2, hy - 4, METAL)
    put(g, hx, hy - 2, ACCENT)
    put(g, hx + (1 if side == "near" else -1), hy, GEM)
    put(g, hx, hy, METAL)


def paint_ferro_blade(g, p):
    """Angular silver sword on the same arc as the arming sword, with a violet edge."""
    x, y = p["hand_m"]
    dx, dy = sword_tip(p)
    if p["anim"] == "attack":
        x0, y0 = x, y
    elif p["view"] == "down":
        x0, y0 = x - 4, y
    elif p["view"] == "up":
        x0, y0 = x + 4, y
    else:
        x0, y0 = x - 6, y - 1
    mag = max((dx * dx + dy * dy) ** 0.5, 1)
    px, py = -dy / mag, dx / mag
    stroke(g, x0 + px * 2, y0 + py * 2, x0 + dx + px * 2, y0 + dy + py * 2, ACCENT, 1)
    stroke(g, x0, y0, x0 + dx, y0 + dy, METAL, 3)
    gx = x0 + dx * 0.18
    gy = y0 + dy * 0.18
    stroke(g, gx - px * 5, gy - py * 3, gx + px * 3, gy + py * 4, TRIM, 2)
    put(g, round(gx), round(gy), GEM)
    stroke(g, x, y, x - dx * 0.16, y - dy * 0.16, TRIM, 2)
    put(g, x0 + dx, y0 + dy, WHITE)
    put(g, x, y, METAL)


PAINTERS = {
    ("body", "base"): paint_body,
    ("arm_far", "base"): lambda g, p: paint_arm(g, p, "far"),
    ("arm_near", "base"): lambda g, p: paint_arm(g, p, "near"),
    ("hair", "short"): lambda g, p: paint_hair(g, p, "short"),
    ("hair", "long"): lambda g, p: paint_hair(g, p, "long"),
    ("hair", "hair_long_streak"): paint_hair_streak,
    ("head", "cap"): paint_cap,
    ("head", "mail_coif"): paint_coif,
    ("head", "helm_plain"): paint_helm,
    ("head", "veris_circlet"): paint_circlet,
    ("chest", "tunic"): paint_tunic,
    ("chest", "hauberk"): paint_hauberk,
    ("chest", "plate"): paint_plate,
    ("chest", "veris_vest_plate"): paint_veris_vest,
    ("sleeve_far", "tunic"): lambda g, p: paint_sleeve(g, p, "tunic", "far"),
    ("sleeve_far", "hauberk"): lambda g, p: paint_sleeve(g, p, "hauberk", "far"),
    ("sleeve_far", "plate"): lambda g, p: paint_sleeve(g, p, "plate", "far"),
    ("sleeve_far", "veris_vest_plate"): lambda g, p: paint_veris_sleeve(g, p, "far"),
    ("sleeve_near", "tunic"): lambda g, p: paint_sleeve(g, p, "tunic", "near"),
    ("sleeve_near", "hauberk"): lambda g, p: paint_sleeve(g, p, "hauberk", "near"),
    ("sleeve_near", "plate"): lambda g, p: paint_sleeve(g, p, "plate", "near"),
    ("sleeve_near", "veris_vest_plate"): lambda g, p: paint_veris_sleeve(g, p, "near"),
    ("legs", "trousers"): paint_trousers,
    ("legs", "mail_chausses"): paint_chausses,
    ("legs", "greaves"): paint_greaves,
    ("legs", "veris_greaves"): paint_veris_greaves,
    ("feet", "boots"): paint_boots,
    ("feet", "mail_boots"): paint_mail_boots,
    ("feet", "sabatons"): paint_sabatons,
    ("feet", "veris_heeled_boots"): paint_veris_boots,
    ("hand_far", "hand_wraps"): lambda g, p: paint_wraps(g, p, "far"),
    ("hand_far", "gloves"): lambda g, p: paint_gloves(g, p, "far"),
    ("hand_far", "gauntlets"): lambda g, p: paint_gauntlets(g, p, "far"),
    ("hand_far", "veris_gauntlets"): lambda g, p: paint_veris_gauntlet(g, p, "far"),
    ("hand_near", "hand_wraps"): lambda g, p: paint_wraps(g, p, "near"),
    ("hand_near", "gloves"): lambda g, p: paint_gloves(g, p, "near"),
    ("hand_near", "gauntlets"): lambda g, p: paint_gauntlets(g, p, "near"),
    ("hand_near", "veris_gauntlets"): lambda g, p: paint_veris_gauntlet(g, p, "near"),
    ("back", "cape"): paint_cape,
    ("back", "cloak"): paint_cloak,
    ("back", "quiver"): paint_quiver,
    ("back", "veris_longcoat"): paint_veris_coat,
    ("main", "sword"): paint_sword,
    ("main", "ferro_blade"): paint_ferro_blade,
    ("main", "bow"): paint_bow,
    ("main", "pistol"): paint_pistol,
    ("off", "shield"): paint_shield,
    ("off", "tome"): paint_tome,
    ("off", "lantern"): paint_lantern,
}

GEAR_SLOTS = ("head", "chest", "legs", "feet", "hands", "back", "main", "off")


def shade(mask, darken=False):
    """Material id to palette index, light from the top left, 1 px outline."""
    idx = [[0] * N for _ in range(N)]

    def at(x, y):
        if 0 <= x < N and 0 <= y < N:
            return mask[y][x]
        return 0

    for y in range(N):
        row = mask[y]
        out = idx[y]
        for x in range(N):
            m = row[x]
            if not m:
                continue
            if m in (EYE, WHITE):
                out[x] = m * 5 + 3
                continue
            lit = at(x - 1, y) != m or at(x, y - 1) != m
            far1 = at(x + 1, y) != m or at(x, y + 1) != m
            far2 = at(x + 2, y) != m or at(x, y + 2) != m
            step = 3
            if far1 and not lit:
                step = 1 if m in (METAL, TRIM) else 2
            elif far2 and not lit and (x + y) % 2 == 0:
                step = 2
            elif lit and not far1:
                step = 4
            if darken and step > 1:
                step -= 1
            out[x] = m * 5 + step
    for y in range(N):
        for x in range(N):
            if mask[y][x] or idx[y][x]:
                continue
            nb = 0
            for xx, yy in ((x, y - 1), (x - 1, y), (x, y + 1), (x + 1, y)):
                if 0 <= xx < N and 0 <= yy < N and mask[yy][xx]:
                    nb = mask[yy][xx]
                    break
            if nb:
                idx[y][x] = nb * 5
    return idx


def mirror_grid(idx):
    return [list(reversed(row)) for row in idx]


def blit(sheet, frame, col, row):
    ox = col * N
    oy = row * N
    for y in range(N):
        dest = sheet[oy + y]
        src = frame[y]
        dest[ox : ox + N] = src


def cell(sheet, col, row):
    ox = col * N
    oy = row * N
    return [sheet[oy + y][ox : ox + N] for y in range(N)]


def empty_cell(sheet, col, row):
    ox = col * N
    oy = row * N
    for y in range(N):
        if any(sheet[oy + y][ox : ox + N]):
            return False
    return True


def nearest(mask, x, y, rad):
    x = int(x)
    y = int(y)
    for dy in range(-rad, rad + 1):
        yy = y + dy
        if yy < 0 or yy >= N:
            continue
        row = mask[yy]
        for dx in range(-rad, rad + 1):
            xx = x + dx
            if 0 <= xx < N and row[xx]:
                return True
    return False


def anchor_set(mask, x, y):
    x, y = int(x), int(y)
    return 0 <= x < N and 0 <= y < N and mask[y][x] != 0


def check_mask(slot, mask, pose):
    """Anchors are the contract. A miss here is layer drift."""
    problems = []
    label = f"{slot} {pose['anim']} {pose['view']} f{pose['frame']}"
    if slot == "body":
        points = (
            ("head", pose["head"], 0),
            ("chest", pose["chest"], 1),
        )
        for name, pt, rad in points:
            if not nearest(mask, pt[0], pt[1], rad):
                problems.append(f"{label}: {name} {pt} empty")
        for name in ("foot_m", "foot_o"):
            if not anchor_set(mask, pose[name][0], pose[name][1]):
                problems.append(f"{label}: {name} sole off {pose[name]}")
    elif slot == "hair":
        hx, hy = pose["head"]
        if not nearest(mask, hx, hy - 6, 2):
            problems.append(f"{label}: hair off the crown")
    elif slot == "head":
        hx, hy = pose["head"]
        if not nearest(mask, hx, hy - 7, 2):
            problems.append(f"{label}: head piece off the crown")
    elif slot == "chest":
        if not nearest(mask, pose["chest"][0], pose["chest"][1], 1):
            problems.append(f"{label}: chest anchor empty")
    elif slot == "legs":
        if not nearest(mask, pose["hip"][0], pose["hip"][1] + 2, 2):
            problems.append(f"{label}: hip anchor empty")
    elif slot == "feet":
        for name in ("foot_m", "foot_o"):
            if not anchor_set(mask, pose[name][0], pose[name][1]):
                problems.append(f"{label}: {name} sole off {pose[name]}")
    elif slot in ("arm_far", "hand_far"):
        if not nearest(mask, pose["hand_m"][0], pose["hand_m"][1], 0):
            problems.append(f"{label}: far grip empty")
    elif slot in ("arm_near", "hand_near"):
        if not nearest(mask, pose["hand_o"][0], pose["hand_o"][1], 0):
            problems.append(f"{label}: near grip empty")
    elif slot == "sleeve_far":
        if not nearest(mask, pose["shoulder_m"][0], pose["shoulder_m"][1], 1):
            problems.append(f"{label}: far sleeve off the shoulder")
    elif slot == "sleeve_near":
        if not nearest(mask, pose["shoulder_o"][0], pose["shoulder_o"][1], 1):
            problems.append(f"{label}: near sleeve off the shoulder")
    elif slot == "back":
        if not nearest(mask, pose["neck"][0] + (6 if pose["view"] == "left" else 0), pose["neck"][1], 4):
            problems.append(f"{label}: back off the shoulders")
    elif slot == "main":
        if not nearest(mask, pose["hand_m"][0], pose["hand_m"][1], 0):
            problems.append(f"{label}: grip empty")
    elif slot == "off":
        if not nearest(mask, pose["hand_o"][0], pose["hand_o"][1], 0):
            problems.append(f"{label}: off grip empty")
    count = sum(1 for row in mask for v in row if v)
    if count < 8:
        problems.append(f"{label}: only {count} pixels")
    return problems


def save_indexed(index, path):
    height = len(index)
    width = len(index[0])
    im = Image.new("P", (width, height))
    palette = []
    for i in range(256):
        if i == 0:
            palette.extend((0, 0, 0))
        else:
            palette.extend((i, 0, 1))
    im.putpalette(palette)
    im.putdata([index[y][x] for y in range(height) for x in range(width)])
    im.save(path, transparency=0, optimize=False)
    check = Image.open(path)
    if check.mode != "P" or check.size != (width, height):
        raise RuntimeError(f"bad indexed png {path}")
    # Spot-check that the file kept the index in the pixel, not a blended color.
    sample = None
    for y, row in enumerate(index):
        for x, value in enumerate(row):
            if value:
                sample = (x, y, value)
                break
        if sample:
            break
    if sample and check.getpixel((sample[0], sample[1])) != sample[2]:
        raise RuntimeError(f"index roundtrip failed for {path}")


def build_table(base_map):
    colors = [(0, 0, 0, 0) for _ in range(65)]
    dark = (22, 17, 28)
    for material, hex_color in base_map.items():
        base = H(hex_color)
        hi, mid, sh, deep = ramp(base)
        outline = tuple(int(dark[i] * 0.8 + base[i] * 0.2) for i in range(3))
        for step, rgb in enumerate((outline, deep, sh, mid, hi)):
            colors[material * 5 + step] = rgb + (255,)
    return colors


def hex_color(color):
    r, g, b, a = color
    return f"#{r:02x}{g:02x}{b:02x}{a:02x}"


VARIANTS = (
    ("steel", "Steel", pal(cloth="#4A5878", cloth2="#C8372E")),
    ("gilded", "Gilded", pal(metal="#E2E6EE", trim="#C99A3A", cloth="#3D5A9C", cloth2="#C8372E")),
    ("moss", "Moss", pal(metal="#C5CDB0", trim="#4E6E34", cloth="#3F5A2A", cloth2="#C99A3A", leather="#4A3820")),
    ("crimson", "Crimson", pal(metal="#4A4450", trim="#C8372E", cloth="#7A1E2A", cloth2="#E0B040", leather="#4A2420")),
    ("veris", "Veris", pal(
        skin="#F0D2C2",
        hair="#1B1D26",
        eye="#C9B6FF",
        cloth="#1B1D26",
        cloth2="#232634",
        metal="#B9BCC6",
        trim="#5D5F6B",
        leather="#232634",
        accent="#B794FF",
        white="#E4E2EE",
        gem="#5B4A8A",
    )),
)


def colorize(index, table):
    height = len(index)
    width = len(index[0])
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    px = img.load()
    for y in range(height):
        row = index[y]
        for x in range(width):
            value = row[x]
            if value:
                px[x, y] = table[value]
    return img


def order_for(anim, view, frame):
    facing = "left" if view == "right" else view
    override = ORDER_OVERRIDES.get(anim, {}).get(facing, {}).get(str(frame))
    if override:
        return override
    return ORDER[facing]


def composite(sheets, loadout, anim, view, frame, table):
    row = {"idle": 0, "walk": 4, "attack": 8}[anim] + DIRS.index(view)
    img = Image.new("RGBA", (N, N), (0, 0, 0, 0))
    head = loadout.get("head")
    for slot in order_for(anim, view, frame):
        if slot in ("body", "arm_far", "arm_near"):
            item = "base"
        elif slot == "hair":
            if head in HIDES_HAIR:
                continue
            item = loadout.get("hair")
        elif slot in ("sleeve_far", "sleeve_near"):
            item = loadout.get("chest")
        elif slot in ("hand_far", "hand_near"):
            item = loadout.get("hands")
        else:
            item = loadout.get(slot)
        if not item:
            continue
        piece = cell(sheets[(slot, item)], frame, row)
        img.alpha_composite(colorize(piece, table))
    return img


def bake_sheets():
    os.makedirs(OUT, exist_ok=True)
    problems = []
    sheets = {}
    for (slot, item), painter in PAINTERS.items():
        sheet = [[0] * (8 * N) for _ in range(12 * N)]
        for anim, count, _fps in ANIMS:
            row0 = {"idle": 0, "walk": 4, "attack": 8}[anim]
            for frame in range(count):
                for di, view in enumerate(("down", "left", "up")):
                    pose = make_pose(anim, view, frame)
                    mask = grid()
                    painter(mask, pose)
                    problems.extend(check_mask(slot, mask, pose))
                    darker = slot in ("arm_far", "sleeve_far", "hand_far") and view == "left"
                    idx = shade(mask, darken=darker)
                    blit(sheet, idx, frame, row0 + di)
                    if view == "left":
                        blit(sheet, mirror_grid(idx), frame, row0 + 3)
        # Unused attack and idle cells stay clear. Walk fills the row.
        for row in list(range(0, 4)) + list(range(8, 12)):
            start = 4 if row < 4 else 6
            for col in range(start, 8):
                if not empty_cell(sheet, col, row):
                    problems.append(f"{slot}/{item}: cell {col},{row} should be empty")
        for frame in range(8):
            for row0 in (0, 4, 8):
                if row0 == 0 and frame > 3:
                    continue
                if row0 == 8 and frame > 5:
                    continue
                left = cell(sheet, frame, row0 + 1)
                right = cell(sheet, frame, row0 + 3)
                mirrored = mirror_grid(left)
                if mirrored != right:
                    problems.append(f"{slot}/{item}: right row is not a mirror ({row0} f{frame})")
                    break
        folder = os.path.join(OUT, slot)
        os.makedirs(folder, exist_ok=True)
        save_indexed(sheet, os.path.join(folder, f"{item}.png"))
        sheets[(slot, item)] = sheet
        print(f"sheet {slot}/{item}")
    return sheets, problems


def write_palettes(tables):
    for slot, item in PAINTERS:
        for vid, _name, _colors in VARIANTS:
            folder = os.path.join(OUT, "palettes", slot, item)
            os.makedirs(folder, exist_ok=True)
            payload = {
                "id": vid,
                "name": dict((key, label) for key, label, _src in VARIANTS)[vid],
                "slot": slot,
                "item": item,
                "colors": [hex_color(c) for c in tables[vid]],
            }
            with open(os.path.join(folder, f"{vid}.json"), "w", encoding="utf-8") as fh:
                json.dump(payload, fh, indent=1)
                fh.write("\n")


def write_manifest(tables):
    def items_for(slot):
        if slot == "hands":
            return [{"id": item, "name": NAMES[item]} for item in ("hand_wraps", "gloves", "gauntlets", "veris_gauntlets")]
        found = []
        for s, item in PAINTERS:
            if s == slot and slot != "body":
                found.append({"id": item, "name": NAMES[item]})
        return found

    slots = []
    for slot, label, optional in (
        ("hair", "Hair", False),
        ("head", "Head", True),
        ("chest", "Chest", True),
        ("legs", "Legs", True),
        ("feet", "Feet", True),
        ("hands", "Hands", True),
        ("back", "Back", True),
        ("main", "Main hand", True),
        ("off", "Off hand", True),
    ):
        slots.append({"id": slot, "name": label, "optional": optional, "items": items_for(slot)})
    manifest = {
        "frame": N,
        "columns": 8,
        "rows": 12,
        "pivot": [32, 60],
        "directions": list(DIRS),
        "anims": {
            "idle": {"row": 0, "frames": 4, "fps": 6},
            "walk": {"row": 4, "frames": 8, "fps": 12},
            "attack": {"row": 8, "frames": 6, "fps": 16},
        },
        "order": {**ORDER, "right": ORDER["left"]},
        "orderOverrides": ORDER_OVERRIDES,
        "hidesHair": list(HIDES_HAIR),
        "twoHand": list(TWO_HAND),
        "slots": slots,
        "sheets": [
            {"slot": slot, "item": item, "file": f"{slot}/{item}.png"}
            for slot, item in PAINTERS
        ],
        "variants": [
            {"id": vid, "name": label, "colors": [hex_color(c) for c in tables[vid]]}
            for vid, label, _src in VARIANTS
        ],
        "presets": [
            {
                "id": "light",
                "name": "Light ranger",
                "variant": "moss",
                "loadout": {
                    "hair": "short",
                    "head": "cap",
                    "chest": "tunic",
                    "legs": "trousers",
                    "feet": "boots",
                    "hands": "hand_wraps",
                    "back": "quiver",
                    "main": "bow",
                },
            },
            {
                "id": "mail",
                "name": "Mail and tome",
                "variant": "steel",
                "loadout": {
                    "hair": "long",
                    "head": "mail_coif",
                    "chest": "hauberk",
                    "legs": "mail_chausses",
                    "feet": "mail_boots",
                    "hands": "gloves",
                    "back": "cloak",
                    "main": "sword",
                    "off": "tome",
                },
            },
            {
                "id": "heavy",
                "name": "Heavy knight",
                "variant": "gilded",
                "loadout": {
                    "hair": "short",
                    "head": "helm_plain",
                    "chest": "plate",
                    "legs": "greaves",
                    "feet": "sabatons",
                    "hands": "gauntlets",
                    "back": "cape",
                    "main": "sword",
                    "off": "shield",
                },
            },
            {
                "id": "tinker",
                "name": "Tinker",
                "variant": "crimson",
                "loadout": {
                    "hair": "short",
                    "head": "cap",
                    "chest": "tunic",
                    "legs": "trousers",
                    "feet": "boots",
                    "hands": "gloves",
                    "back": "cloak",
                    "main": "pistol",
                    "off": "lantern",
                },
            },
            {
                "id": "veris",
                "name": "Veris",
                "variant": "veris",
                "loadout": {
                    "hair": "hair_long_streak",
                    "head": "veris_circlet",
                    "chest": "veris_vest_plate",
                    "legs": "veris_greaves",
                    "feet": "veris_heeled_boots",
                    "hands": "veris_gauntlets",
                    "back": "veris_longcoat",
                    "main": "ferro_blade",
                },
            },
        ],
    }
    with open(os.path.join(OUT, "manifest.json"), "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=1)
        fh.write("\n")
    return manifest


def font(size):
    return ImageFont.truetype(FONT_PATH, size)


def filmstrip(sheets, tables, manifest):
    """Full-size strips for visual QA. Not shipped as game art."""
    qa = os.path.join("/tmp", "doll-qa")
    os.makedirs(qa, exist_ok=True)
    presets = manifest["presets"]
    label_h = 18
    for anim, count, _fps in ANIMS:
        width = count * N
        height = (N + label_h) * len(presets) * len(DIRS)
        img = Image.new("RGBA", (width, height), (18, 22, 30, 255))
        draw = ImageDraw.Draw(img)
        pen = font(12)
        y = 0
        for preset in presets:
            table = tables[preset["variant"]]
            for view in DIRS:
                draw.text((4, y + 2), f"{preset['name']}  {anim}  {view}", fill=(243, 239, 228, 255), font=pen)
                y += label_h
                for frame in range(count):
                    frame_img = composite(sheets, preset["loadout"], anim, view, frame, table)
                    # Ground line at the foot baseline so a floating sole is obvious.
                    for x in range(N):
                        r, g, b, a = frame_img.getpixel((x, 60))
                        if a < 40:
                            frame_img.putpixel((x, 60), (70, 120, 90, 255))
                    img.alpha_composite(frame_img, (frame * N, y))
                y += N
        img.save(os.path.join(qa, f"{anim}.png"))
        print("preview", os.path.join(qa, f"{anim}.png"))


def contact_sheet(sheets, tables):
    """Half-scale sheet of the 24 gear items, colored with the Steel table."""
    gear = [
        (slot, item) for slot, item in (
            ("head", "cap"), ("head", "mail_coif"), ("head", "helm_plain"),
            ("chest", "tunic"), ("chest", "hauberk"), ("chest", "plate"),
            ("legs", "trousers"), ("legs", "mail_chausses"), ("legs", "greaves"),
            ("feet", "boots"), ("feet", "mail_boots"), ("feet", "sabatons"),
            ("hand_near", "hand_wraps"), ("hand_near", "gloves"), ("hand_near", "gauntlets"),
            ("back", "cloak"), ("back", "quiver"), ("back", "cape"),
            ("main", "sword"), ("main", "bow"), ("main", "pistol"),
            ("off", "shield"), ("off", "tome"), ("off", "lantern"),
        )
    ]
    if len(gear) != 24:
        raise RuntimeError(f"expected 24 gear sheets, found {len(gear)}")
    table = tables["steel"]
    cols = 4
    scale = 0.5
    cell_w = int(8 * N * scale)
    cell_h = int(12 * N * scale)
    pad = 22
    rows = (len(gear) + cols - 1) // cols
    img = Image.new("RGBA", (cols * cell_w, rows * (cell_h + pad) + 28), (14, 18, 26, 255))
    draw = ImageDraw.Draw(img)
    pen = font(14)
    small = font(11)
    draw.text((8, 6), "FerVois paper doll, 24 item sheets (half scale, Steel)", fill=(243, 239, 228, 255), font=pen)
    for i, (slot, item) in enumerate(gear):
        colored = colorize(sheets[(slot, item)], table)
        thumb = colored.resize((cell_w, cell_h), Image.Resampling.NEAREST)
        c = i % cols
        r = i // cols
        x = c * cell_w
        y = 28 + r * (cell_h + pad)
        img.alpha_composite(thumb, (x, y))
        draw.text((x + 4, y + cell_h + 2), f"{slot}/{item}", fill=(198, 210, 220, 255), font=small)
    path = os.path.join(OUT, "contact-sheet.png")
    img.save(path)
    print("contact", path, img.size)


VERIS_LOADOUT = {
    "hair": "hair_long_streak",
    "head": "veris_circlet",
    "chest": "veris_vest_plate",
    "legs": "veris_greaves",
    "feet": "veris_heeled_boots",
    "hands": "veris_gauntlets",
    "back": "veris_longcoat",
    "main": "ferro_blade",
}

VERIS_STILLS = (
    ("hair", "hair_long_streak"),
    ("head", "veris_circlet"),
    ("chest", "veris_vest_plate"),
    ("sleeve_far", "veris_vest_plate"),
    ("sleeve_near", "veris_vest_plate"),
    ("legs", "veris_greaves"),
    ("feet", "veris_heeled_boots"),
    ("hand_far", "veris_gauntlets"),
    ("hand_near", "veris_gauntlets"),
    ("back", "veris_longcoat"),
    ("main", "ferro_blade"),
)


def export_veris_stills():
    """Idle four-facing stills for the concept folder. sheets.py and doll.py both call this."""
    table = build_table(next(src for vid, _name, src in VARIANTS if vid == "veris"))
    root = os.path.join(HERE, "layers")
    for slot, item in VERIS_STILLS:
        folder = os.path.join(root, slot)
        os.makedirs(folder, exist_ok=True)
        for view in DIRS:
            facing = "left" if view == "right" else view
            pose = make_pose("idle", facing, 0)
            mask = grid()
            PAINTERS[(slot, item)](mask, pose)
            darker = slot in ("sleeve_far", "hand_far") and facing == "left"
            idx = shade(mask, darken=darker)
            if view == "right":
                idx = mirror_grid(idx)
            colorize(idx, table).save(os.path.join(folder, f"{item}_{view}.png"))
    print("veris stills", len(VERIS_STILLS) * len(DIRS))


def veris_contact(sheets, tables):
    """Idle, walk, and attack in four directions, on a mid ground so the black coat reads."""
    table = tables["veris"]
    scale = 2
    groups = (("idle", 4), ("walk", 8), ("attack", 6))
    gap = 10
    label_w = 52
    width = label_w + sum(count * N * scale for _name, count in groups) + gap * (len(groups) - 1)
    height = 36 + len(DIRS) * N * scale
    img = Image.new("RGBA", (width, height), (122, 114, 102, 255))
    draw = ImageDraw.Draw(img)
    pen = font(14)
    small = font(12)
    draw.text((8, 8), "Veris, idle walk attack, down left up right", fill=(243, 239, 228, 255), font=pen)
    x = label_w
    for name, count in groups:
        draw.text((x, 20), name, fill=(28, 26, 24, 255), font=small)
        x += count * N * scale + gap
    for ri, view in enumerate(DIRS):
        y = 36 + ri * N * scale
        draw.text((6, y + 8), view, fill=(243, 239, 228, 255), font=small)
        x = label_w
        for name, count in groups:
            for frame in range(count):
                piece = composite(sheets, VERIS_LOADOUT, name, view, frame, table)
                big = piece.resize((N * scale, N * scale), Image.Resampling.NEAREST)
                img.alpha_composite(big, (x, y))
                x += N * scale
            x += gap
    path = os.path.join(OUT, "veris-contact.png")
    img.save(path)
    print("veris contact", path, img.size)
    return path


def veris_walk_gif(sheets, tables):
    table = tables["veris"]
    scale = 3
    label_w = 56
    width = label_w + N * scale
    height = len(DIRS) * N * scale
    frames = []
    small = font(13)
    for frame in range(8):
        img = Image.new("RGBA", (width, height), (122, 114, 102, 255))
        draw = ImageDraw.Draw(img)
        for ri, view in enumerate(DIRS):
            y = ri * N * scale
            draw.text((6, y + 6), view, fill=(243, 239, 228, 255), font=small)
            piece = composite(sheets, VERIS_LOADOUT, "walk", view, frame, table)
            big = piece.resize((N * scale, N * scale), Image.Resampling.NEAREST)
            img.alpha_composite(big, (label_w, y))
        frames.append(img.convert("RGB"))
    path = os.path.join(OUT, "veris-walk.gif")
    frames[0].save(path, save_all=True, append_images=frames[1:], duration=90, loop=0, disposal=2)
    print("veris gif", path)
    return path


def main():
    tables = {vid: build_table(src) for vid, _label, src in VARIANTS}
    sheets, problems = bake_sheets()
    write_palettes(tables)
    manifest = write_manifest(tables)
    filmstrip(sheets, tables, manifest)
    contact_sheet(sheets, tables)
    export_veris_stills()
    veris_contact(sheets, tables)
    veris_walk_gif(sheets, tables)
    if problems:
        print(f"{len(problems)} alignment problems")
        for line in problems[:40]:
            print(" -", line)
        sys.exit(1)
    print("ok", len(sheets), "sheets")


if __name__ == "__main__":
    main()
