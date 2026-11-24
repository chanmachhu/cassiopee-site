#!/usr/bin/env python3
"""Generate the mythology artboard: hand-built SVG drawings (columns, ivy, pediment) inlined in the page."""
import json
import math
import random
import sys
from string import Template

TS_MODE = sys.argv[1] == "--ts"
OUT = sys.argv[2] if TS_MODE else sys.argv[1]


def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def smooth(pts):
    d = f"M{n(pts[0][0])},{n(pts[0][1])}"
    for i in range(len(pts) - 1):
        p0 = pts[i - 1] if i else pts[i]
        p1, p2 = pts[i], pts[i + 1]
        p3 = pts[i + 2] if i + 2 < len(pts) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f" C{n(c1[0])},{n(c1[1])} {n(c2[0])},{n(c2[1])} {n(p2[0])},{n(p2[1])}"
    return d


# ---------- ivy ----------
FRONT = ["lfA", "lfA", "lfB", "lfC", "lfA", "lfD", "lfC"]
LEAF = ("M0,0 C-4,2 -11,4 -16,1 C-19,-1 -18,-6 -14,-9 C-17,-11 -22,-15 -22,-20 C-21,-23 -14,-25 -9,-24 "
        "C-9,-31 -4,-37 0,-40 C4,-37 9,-31 9,-24 C14,-25 21,-23 22,-20 C22,-15 17,-11 14,-9 C18,-6 19,-1 16,1 C11,4 4,2 0,0Z")
SHEEN = "M0,-2 C-6,-6 -14,-12 -19,-19 C-12,-20 -8,-22 -6,-25 C-4,-30 -2,-34 0,-37Z"
VEINS = ("M0,0 Q.6,-19 0,-36 M0,-2 Q-9,-8 -18,-19 M0,-2 Q9,-8 18,-19 M0,0 Q-7,0 -14,0 "
         "M0,0 Q7,0 14,0 M0,-15 Q-3,-18 -5,-24 M0,-15 Q3,-18 5,-24 M-8,-8 Q-11,-8 -14,-5 M8,-8 Q11,-8 14,-5")


def anim(d):
    """Growth timing: d is the delay in seconds, None keeps the element static."""
    return "" if d is None else f' style="--d:{d:.2f}s"'


def leaf(x, y, ang, s, fill="lfA", vein="#DDE8CB", fx=1.0, d=None):
    t = f"translate({n(x)} {n(y)})"
    if abs(fx - 1) > 0.03:
        t += f" scale({n(fx)} 1)"
    t += f" rotate({n(ang)}) scale({n(s)})"
    if d is None:
        return f'<use href="#leaf" transform="{t}" fill="url(#{fill})" color="{vein}"/>'
    # the animated group sits at the stalk, so the leaf unfurls from it
    return f'<g transform="{t}"><g class="lf"{anim(d)}><use href="#leaf" fill="url(#{fill})" color="{vein}"/></g></g>'


def back_leaf(x, y, ang, s, fx=0.7, d=None):
    return leaf(x, y, ang, s, "lfBack", "#7A8C6B", fx, d)


def stem(pts, w, back=False, d=None, t=1.0):
    p = smooth(pts)
    g = "" if d is None else f' pathLength="1" class="st" style="--d:{d:.2f}s;--t:{max(t, .15):.2f}s"'
    if back:
        return f'<path d="{p}" fill="none" stroke="#2E2418" stroke-width="{n(w)}" stroke-linecap="round"{g}/>'
    return (f'<path d="{p}" fill="none" stroke="#47362A" stroke-width="{n(w)}" stroke-linecap="round"{g}/>'
            f'<path d="{p}" fill="none" stroke="#9A8060" stroke-width="{n(w * .3)}" stroke-linecap="round" '
            f'transform="translate({n(-w * .2)} {n(-w * .2)})"{g}/>')


def rootlets(pts, rnd, scale, d=None):
    segs = []
    for i in range(1, len(pts) - 1, 2):
        x, y = pts[i][:2]
        for _ in range(rnd.randint(2, 4)):
            a = rnd.uniform(0, 2 * math.pi)
            ln = rnd.uniform(1.2, 3.2) * scale
            segs.append(f"M{n(x)},{n(y)}l{n(ln * math.cos(a))},{n(ln * math.sin(a))}")
    cls = "" if d is None else f' class="fd"{anim(d)}'
    return (f'<path d="{"".join(segs)}" stroke="#6E5A40" stroke-width="{n(.45 * scale)}" '
            f'stroke-linecap="round" opacity=".75"{cls}/>')


def at(d0, dur, t):
    return None if d0 is None else d0 + dur * t


def helix(cx, r, y0, y1, turns, seed, s0, phase=0.0, w0=2.4, w1=1.1, per_turn=8, scale=1.0, d0=None, dur=2.0):
    """Ivy wound around a column: back runs and peeking leaves, then front runs and leaves sorted by depth."""
    rnd = random.Random(seed)
    N = max(16, int(turns * 36))
    pts = []
    for i in range(N + 1):
        t = i / N
        phi = phase + t * turns * 2 * math.pi
        rr = r * (1.08 + .05 * math.sin(t * 13 + seed))
        x = cx + rr * math.sin(phi) + r * .05 * math.sin(t * 31 + seed * 1.3)
        pts.append((x, y0 + (y1 - y0) * t, phi, t))
    back, front, bl, fl = [], [], [], []

    def flush(run, is_front):
        if len(run) < 2:
            return
        ta, tb = run[0][3], run[-1][3]
        w = (w0 + (w1 - w0) * (ta + tb) / 2) * scale
        pl = [(p[0], p[1]) for p in run]
        d, t = at(d0, dur, ta), dur * (tb - ta)
        if is_front:
            front.append(stem(pl, w, d=d, t=t))
            front.append(rootlets(pl, rnd, scale, at(d0, dur, tb)))
        else:
            back.append(stem(pl, w * .8, back=True, d=d, t=t))

    run, fr = [pts[0]], math.cos(pts[0][2]) > 0
    for p in pts[1:]:
        f = math.cos(p[2]) > 0
        run.append(p)
        if f != fr:
            flush(run, fr)
            run, fr = [p], f
    flush(run, fr)
    step = max(1, round(N / (turns * per_turn)))
    side = 1
    for i in range(1, N + 1, step):
        x, y, phi, t = pts[i]
        c, sn = math.cos(phi), math.sin(phi)
        side = -side
        s = s0 * (1 - .4 * t) * rnd.uniform(.82, 1.15)
        d = at(d0, dur, t + .04)
        if c > -.15:
            ang = math.copysign(rnd.uniform(45, 95), sn) if abs(sn) > .65 else side * rnd.uniform(20, 70)
            fl.append((c, leaf(x, y, ang, s * (.88 + .12 * max(c, 0)), rnd.choice(FRONT), fx=.55 + .45 * max(c, 0), d=d)))
        elif abs(sn) > .7:
            bl.append(back_leaf(x, y, math.copysign(rnd.uniform(55, 100), sn), s * .82, .62, d=d))
    fl.sort(key=lambda e: e[0])
    return "".join(back + bl), "".join(front) + "".join(l for _, l in fl)


def clump(cx, y, half, seed, s, count=14, d0=None):
    """Ivy tuft at the foot of a column; back leaves stick out on the sides."""
    rnd = random.Random(seed)
    back, front = [], []
    for k in range(count):
        d = None if d0 is None else d0 + rnd.uniform(.1, .7)
        if k % 3 == 0:
            sd = 1 if k % 2 else -1
            x = cx + sd * half * rnd.uniform(.75, 1.05)
            back.append(back_leaf(x, y - rnd.uniform(4, 22) * s * 2, sd * rnd.uniform(40, 85), s * rnd.uniform(.75, 1), .75, d=d))
        else:
            x = cx + rnd.uniform(-half, half)
            yy = y - rnd.uniform(0, 26) * s
            ang = rnd.uniform(-55, 55) + (x - cx) / half * 30
            front.append((yy, leaf(x, yy, ang, s * rnd.uniform(.8, 1.15), rnd.choice(FRONT), d=d)))
    front.sort(key=lambda e: e[0])
    stems = []
    for k in range(3):
        x = cx + rnd.uniform(-half * .8, half * .8)
        stems.append(stem([(x, y + 2), (x + rnd.uniform(-6, 6) * s, y - 14 * s), (x + rnd.uniform(-10, 10) * s, y - 30 * s)],
                          1.6 * s * 2, d=d0, t=.5))
    return "".join(back), "".join(stems) + "".join(l for _, l in front)


def pendant(x0, y0, L, seed, s, sway=8, count=7, w=1.5, drift=0, d0=None, dur=1.2, swing=None):
    """Hanging strand; with swing (seconds) it sways in the wind around its top."""
    rnd = random.Random(seed)
    N = 18
    pts = [(x0 + drift * (i / N) + sway * math.sin(i / N * 5.2 + seed) * (i / N), y0 + L * i / N) for i in range(N + 1)]
    out = [stem(pts, w, d=d0, t=dur)]
    side = 1
    for k in range(count):
        i = 1 + round(k * (N - 2) / max(1, count - 1))
        x, y = pts[i]
        side = -side
        out.append(leaf(x, y, side * rnd.uniform(110, 165), s * (1 - .45 * i / N) * rnd.uniform(.85, 1.1), rnd.choice(FRONT),
                        d=at(d0, dur, i / N)))
    body = "".join(out)
    if swing:
        return f'<g class="sway" style="transform-origin:{n(x0)}px {n(y0)}px;--sw:{swing}s">{body}</g>'
    return body


def strand(pts, seed, s, w=2.0, back=False, up=False, every=1, hang=False, d0=None, dur=1.0):
    rnd = random.Random(seed)
    out = [stem(pts, w, back, d=d0, t=dur)]
    side = 1
    for i in range(1, len(pts), every):
        x, y = pts[i]
        side = -side
        sc = s * rnd.uniform(.82, 1.12)
        if up:
            ang = rnd.uniform(-55, 55)
        elif hang:
            ang = side * rnd.uniform(95, 150)
        else:
            ang = side * rnd.uniform(35, 95)
        d = at(d0, dur, i / (len(pts) - 1))
        out.append(back_leaf(x, y, ang, sc, .85, d=d) if back else leaf(x, y, ang, sc, rnd.choice(FRONT), d=d))
    return "".join(out)


# ---------- stone ----------
MOSS = ["#5E7650", "#6F8A5C", "#4B6241", "#7C9466"]


def moss(x, y, spread, rnd, count=10, s=1.0):
    blobs = []
    for _ in range(count):
        blobs.append(f'<ellipse cx="{n(x + rnd.gauss(0, spread))}" cy="{n(y + rnd.gauss(0, spread * .3))}" '
                     f'rx="{n(rnd.uniform(1.2, 3.2) * s)}" ry="{n(rnd.uniform(.7, 1.6) * s)}" fill="{rnd.choice(MOSS)}"/>')
    return f'<g filter="url(#fMoss)" opacity=".6">{"".join(blobs)}</g>'


def chip(x, y, rad, rnd):
    k = rnd.randint(5, 7)
    pts = []
    for i in range(k):
        a = 2 * math.pi * i / k + rnd.uniform(-.3, .3)
        rr = rad * rnd.uniform(.55, 1)
        pts.append((x + rr * math.cos(a), y + rr * math.sin(a) * .8))
    d = "M" + " L".join(f"{n(px)},{n(py)}" for px, py in pts) + "Z"
    return (f'<path d="{d}" fill="#fff" opacity=".65" transform="translate({n(rad * .25)} {n(rad * .3)})"/>'
            f'<path d="{d}" fill="#776E5F" opacity=".32"/>')


def spiral(vcx, vcy, u, mirror=False, r1=1.1, dl=1.85, arcs=8):
    r1 *= u
    dl *= u
    sg = -1 if mirror else 1
    d = f"M{n(vcx - sg * (r1 - dl / 2))},{n(vcy)}"
    for k in range(arcs):
        rk = r1 + k * dl
        d += f" a{n(rk)},{n(rk)} 0 0 {0 if mirror else 1} {n(2 * rk * (1 if k % 2 == 0 else -1) * sg)},0"
    return d


def column(cid, cx, top, bottom, r, seed, broken=False):
    """Ionic column: capital (abacus, volutes, eggs, bead and reel), fluted shaft in perspective, attic base."""
    u = r / 30
    rnd = random.Random(seed)
    o = []
    st, sb = top + 38 * u, bottom - 82 * u
    rb = r * 1.04
    shaft = (f"M{n(cx - r)},{n(st)} L{n(cx + r)},{n(st)} Q{n(cx + rb + 1.4 * u)},{n((st + sb) / 2)} {n(cx + rb)},{n(sb)} "
             f"L{n(cx - rb)},{n(sb)} Q{n(cx - rb - 1.4 * u)},{n((st + sb) / 2)} {n(cx - r)},{n(st)}Z")
    o.append(f'<path d="{shaft}" fill="url(#gShaft)"/>')
    ft, fb = top + 54 * u, sb - 6 * u
    for k in range(-5, 6):
        th = math.radians(k * 15)
        w = 6.3 * u * math.cos(th)
        x = cx + r * 1.01 * math.sin(th) - w / 2
        o.append(f'<rect x="{n(x)}" y="{n(ft)}" width="{n(w)}" height="{n(fb - ft)}" rx="{n(w / 2)}" '
                 f'ry="{n(min(w * .8, 4 * u))}" fill="url(#gFlute)"/>')
    o.append(f'<rect x="{n(cx - .62 * r)}" y="{n(st)}" width="{n(.3 * r)}" height="{n(sb - st)}" fill="url(#gSpec)"/>')
    streaks = []
    for _ in range(6):
        x = cx + rnd.uniform(-.85, .75) * r
        streaks.append(f'<rect x="{n(x)}" y="{n(st + 4 * u)}" width="{n(rnd.uniform(2, 6) * u)}" '
                       f'height="{n(rnd.uniform(90, 320) * u)}" fill="url(#gStreak)"/>')
    o.append(f'<g filter="url(#fSoft)">{"".join(streaks)}</g>')
    o.append(f'<rect x="{n(cx - rb)}" y="{n(sb - 150 * u)}" width="{n(2 * rb)}" height="{n(150 * u)}" fill="url(#gGrime)"/>')
    o.append(f'<path d="{shaft}" fill="#fff" filter="url(#fVeins)" opacity=".5"/>')
    o.append(f'<path d="{shaft}" fill="#fff" filter="url(#fGrain)" opacity=".35"/>')
    for _ in range(7):
        k = rnd.randint(-4, 4)
        x = cx + r * math.sin(math.radians(k * 15 + 7.5))
        o.append(chip(x, rnd.uniform(st + 60 * u, sb - 30 * u), rnd.uniform(1.4, 3.2) * u, rnd))
    pits = "".join(f'<circle cx="{n(cx + rnd.uniform(-.9, .9) * r)}" cy="{n(rnd.uniform(st, sb))}" r="{n(rnd.uniform(.35, .9) * u)}"/>'
                   for _ in range(22))
    o.append(f'<g fill="#6F6657" opacity=".35">{pits}</g>')
    o.append(f'<path d="{shaft}" fill="none" stroke="#8F8778" stroke-opacity=".65" stroke-width="{n(.8 * u)}"/>')
    # bead and reel
    ay, ah = top + 40 * u, 7 * u
    o.append(f'<rect x="{n(cx - 31 * u)}" y="{n(ay)}" width="{n(62 * u)}" height="{n(ah)}" rx="{n(ah / 2)}" fill="url(#gTorus)" '
             f'stroke="#9C9485" stroke-opacity=".55" stroke-width="{n(.5 * u)}"/>')
    for k in range(-8, 9):
        a = math.radians(k * 10)
        x, c = cx + 30 * u * math.sin(a), math.cos(a)
        if k % 2 == 0:
            o.append(f'<ellipse cx="{n(x)}" cy="{n(ay + ah / 2)}" rx="{n(2.4 * u * c)}" ry="{n(2.6 * u)}" fill="url(#gBead)" '
                     f'stroke="#A79F90" stroke-width="{n(.3 * u)}"/>')
        else:
            o.append(f'<rect x="{n(x - .6 * u * c)}" y="{n(ay + 1.3 * u)}" width="{n(1.2 * u * c)}" height="{n(ah - 2.6 * u)}" fill="#B5AD9E"/>')
    # echinus with egg and dart
    ech = (f"M{n(cx - 27 * u)},{n(top + 19 * u)} Q{n(cx)},{n(top + 23 * u)} {n(cx + 27 * u)},{n(top + 19 * u)} "
           f"L{n(cx + 25 * u)},{n(top + 40 * u)} Q{n(cx)},{n(top + 43 * u)} {n(cx - 25 * u)},{n(top + 40 * u)}Z")
    o.append(f'<path d="{ech}" fill="url(#gEchinus)"/>')
    eggs = []
    for k in range(-2, 3):
        x = cx + k * 10 * u
        eggs.append(f'<path d="M{n(x - 4.8 * u)},{n(top + 22 * u)} Q{n(x - 5.4 * u)},{n(top + 37 * u)} {n(x)},{n(top + 37.5 * u)} '
                    f'Q{n(x + 5.4 * u)},{n(top + 37 * u)} {n(x + 4.8 * u)},{n(top + 22 * u)}" fill="#E4DED3" stroke="#978F80" '
                    f'stroke-opacity=".7" stroke-width="{n(.6 * u)}"/>')
        eggs.append(f'<ellipse cx="{n(x)}" cy="{n(top + 29.5 * u)}" rx="{n(3.6 * u)}" ry="{n(5.4 * u)}" fill="url(#gEgg)" '
                    f'stroke="#8F8778" stroke-opacity=".6" stroke-width="{n(.5 * u)}"/>')
        xd = x + 5 * u
        if k < 2:
            eggs.append(f'<path d="M{n(xd)},{n(top + 22 * u)} L{n(xd)},{n(top + 35 * u)} M{n(xd - 1.5 * u)},{n(top + 33 * u)} '
                        f'L{n(xd)},{n(top + 37 * u)} L{n(xd + 1.5 * u)},{n(top + 33 * u)}" fill="none" stroke="#7F7768" '
                        f'stroke-width="{n(.7 * u)}"/>')
    o.append(f'<g clip-path="url(#{cid}-ech)">{"".join(eggs)}</g>')
    # canalis
    o.append(f'<path d="M{n(cx - 55 * u)},{n(top + 8 * u)} L{n(cx + 55 * u)},{n(top + 8 * u)} L{n(cx + 55 * u)},{n(top + 20 * u)} '
             f'Q{n(cx)},{n(top + 27 * u)} {n(cx - 55 * u)},{n(top + 20 * u)}Z" fill="url(#gCap)" stroke="#9C9485" '
             f'stroke-opacity=".6" stroke-width="{n(.6 * u)}"/>')
    o.append(f'<path d="M{n(cx - 50 * u)},{n(top + 12 * u)} Q{n(cx)},{n(top + 17 * u)} {n(cx + 50 * u)},{n(top + 12 * u)}" '
             f'fill="none" stroke="#fff" stroke-width="{n(.8 * u)}" opacity=".9"/>')
    # small carved leaves where volutes meet the echinus
    for s in (-1, 1):
        lx = cx + s * 25 * u
        for a in (s * 25, s * 55, s * 85):
            o.append(f'<path d="M0,0 C{n(1.6 * u)},{n(-2 * u)} {n(1.2 * u)},{n(-6 * u)} 0,{n(-8 * u)} C{n(-1.2 * u)},{n(-6 * u)} '
                     f'{n(-1.6 * u)},{n(-2 * u)} 0,0Z" transform="translate({n(lx)} {n(top + 40 * u)}) rotate({a})" '
                     f'fill="url(#gCap)" stroke="#9C9485" stroke-width="{n(.4 * u)}"/>')
    # volutes
    for s in (-1, 1):
        vx, vy = cx + s * 39 * u, top + 30 * u
        o.append(f'<circle cx="{n(vx)}" cy="{n(vy)}" r="{n(16 * u)}" fill="url(#gVolute)" stroke="#8F8778" '
                 f'stroke-opacity=".65" stroke-width="{n(.8 * u)}"/>')
        sp = spiral(vx, vy, u, mirror=s > 0)
        o.append(f'<path d="{sp}" fill="none" stroke="#fff" stroke-width="{n(1 * u)}" opacity=".85" '
                 f'transform="translate({n(.6 * u)} {n(.8 * u)})"/>')
        o.append(f'<path d="{sp}" fill="none" stroke="#7C7465" stroke-width="{n(1.3 * u)}" opacity=".8"/>')
        o.append(f'<circle cx="{n(vx + s * .2 * u)}" cy="{n(vy)}" r="{n(2.3 * u)}" fill="url(#gGold)" stroke="#7F6220" '
                 f'stroke-width="{n(.3 * u)}"/>')
    if broken:
        vx, vy = cx + 39 * u, top + 30 * u
        brk = (f"M{n(vx + 6 * u)},{n(vy - 15 * u)} L{n(vx + 10 * u)},{n(vy - 9 * u)} L{n(vx + 9 * u)},{n(vy - 6 * u)} "
               f"L{n(vx + 13 * u)},{n(vy - 3 * u)} L{n(vx + 16.5 * u)},{n(vy - 4 * u)} L{n(vx + 17 * u)},{n(vy - 16 * u)}Z")
        o.append(f'<path d="{brk}" fill="#F5F3EE"/>')
        o.append(f'<path d="M{n(vx + 6 * u)},{n(vy - 15 * u)} L{n(vx + 10 * u)},{n(vy - 9 * u)} L{n(vx + 9 * u)},{n(vy - 6 * u)} '
                 f'L{n(vx + 13 * u)},{n(vy - 3 * u)} L{n(vx + 16.5 * u)},{n(vy - 4 * u)}" fill="none" stroke="#7C7465" '
                 f'stroke-width="{n(.7 * u)}"/>')
        o.append(f'<path d="M{n(vx + 7 * u)},{n(vy - 13 * u)} L{n(vx + 9.6 * u)},{n(vy - 8.6 * u)} L{n(vx + 8.4 * u)},{n(vy - 6 * u)} '
                 f'L{n(vx + 12 * u)},{n(vy - 2.6 * u)}" fill="none" stroke="#fff" stroke-width="{n(.8 * u)}" opacity=".9"/>')
    # abacus
    o.append(f'<rect x="{n(cx - 57 * u)}" y="{n(top)}" width="{n(114 * u)}" height="{n(8 * u)}" fill="url(#gCap)" '
             f'stroke="#9C9485" stroke-opacity=".7" stroke-width="{n(.6 * u)}"/>')
    o.append(f'<path d="M{n(cx - 56 * u)},{n(top + 5.5 * u)} H{n(cx + 56 * u)}" stroke="#A79F90" stroke-width="{n(.6 * u)}" opacity=".7"/>')
    o.append(f'<path d="M{n(cx - 56 * u)},{n(top + .7 * u)} H{n(cx + 56 * u)}" stroke="#fff" stroke-width="{n(.8 * u)}"/>')
    o.append(f'<path d="M{n(cx - 55 * u)},{n(top + 8.2 * u)} H{n(cx + 55 * u)}" stroke="#A8842F" stroke-width="{n(.7 * u)}" opacity=".75"/>')
    if broken:
        o.append(f'<path d="M{n(cx + 57 * u)},{n(top)} L{n(cx + 49 * u)},{n(top)} L{n(cx + 51 * u)},{n(top + 3 * u)} '
                 f'L{n(cx + 55 * u)},{n(top + 4 * u)} L{n(cx + 57 * u)},{n(top + 8 * u)}Z" fill="#F5F3EE"/>')
    capbox = (f'<rect x="{n(cx - 57 * u)}" y="{n(top)}" width="{n(114 * u)}" height="{n(46 * u)}"/>')
    o.append(f'<g fill="#fff" filter="url(#fGrain)" opacity=".45">{capbox}</g>')
    # attic base
    base = []
    base.append((sb, 4 * u, 1.06 * r, 0, "#E9E4DB"))
    base.append((sb + 4 * u, 14 * u, 1.17 * r, 7 * u, "url(#gTorus)"))
    base.append((sb + 18 * u, 10 * u, 1.06 * r, 0, "url(#gScotia)"))
    base.append((sb + 28 * u, 18 * u, 1.33 * r, 9 * u, "url(#gTorus)"))
    base.append((sb + 46 * u, bottom - sb - 46 * u, 1.48 * r, 0, "url(#gPlinth)"))
    for y, h, hw, rx, fill in base:
        o.append(f'<rect x="{n(cx - hw)}" y="{n(y)}" width="{n(2 * hw)}" height="{n(h)}" rx="{n(rx)}" fill="{fill}" '
                 f'stroke="#958D7E" stroke-opacity=".6" stroke-width="{n(.6 * u)}"/>')
    o.append(f'<path d="M{n(cx - 1.48 * r)},{n(sb + 46.8 * u)} H{n(cx + 1.48 * r)}" stroke="#fff" stroke-width="{n(.9 * u)}"/>')
    o.append(f'<path d="M{n(cx - 1.48 * r)},{n(sb + 46 * u)} l{n(9 * u)},0 l{n(-3 * u)},{n(6 * u)} l{n(-6 * u)},{n(3 * u)}Z" fill="#F5F3EE"/>')
    o.append(f'<path d="M{n(cx - 1.48 * r + 9 * u)},{n(sb + 46 * u)} l{n(-3 * u)},{n(6 * u)} l{n(-6 * u)},{n(3 * u)}" fill="none" '
             f'stroke="#7C7465" stroke-width="{n(.6 * u)}"/>')
    basebox = f'<rect x="{n(cx - 1.48 * r)}" y="{n(sb)}" width="{n(2.96 * r)}" height="{n(bottom - sb)}"/>'
    o.append(f'<g fill="#fff" filter="url(#fGrain)" opacity=".5">{basebox}</g>')
    o.append(moss(cx - 1.25 * r, bottom - 2 * u, 7 * u, rnd, 9, u * 1.4))
    o.append(moss(cx + 1.3 * r, bottom - 3 * u, 6 * u, rnd, 7, u * 1.4))
    o.append(moss(cx - .9 * r, sb + 28 * u, 5 * u, rnd, 5, u))
    group = f'<g id="{cid}">{"".join(o)}</g>'
    clips = (f'<clipPath id="{cid}-ech"><path d="{ech}"/></clipPath>'
             f'<clipPath id="{cid}-clip"><path d="{shaft}"/>{capbox}{basebox}</clipPath>')
    return group + clips


def col_instance(colid, back, front, fid, sd=2.5):
    # the cast shadow fades in once the ivy has grown, never before it
    shadow = (f'<g class="ivy-sh" style="--d:{sd}s" clip-path="url(#{colid}-clip)"><use href="#{fid}" transform="translate(4 5)" filter="url(#fCast)"/></g>'
              if front else "")
    return f'{back}<use href="#{colid}"/>{shadow}<g id="{fid}">{front}</g>'


def palmette(x, y, L, side=0, k=4, spread=78, sw=.7):
    leaves, ribs = [], []
    for i in range(-k, k + 1):
        if (side < 0 < i) or (side > 0 > i):
            continue
        a = i * spread / k + side * 14
        ln = L * (1 - .11 * abs(i))
        w = L * .15 * (1 - .06 * abs(i))
        curl = .12 * ln * ((i > 0) - (i < 0))
        d = (f"M0,0 C{n(w)},{n(-ln * .3)} {n(w * .95 + curl * .5)},{n(-ln * .78)} {n(curl)},{n(-ln)} "
             f"C{n(-w * .7 + curl * .5)},{n(-ln * .8)} {n(-w)},{n(-ln * .3)} 0,0Z")
        tr = f"translate({n(x)} {n(y)}) rotate({n(a)})"
        leaves.append(f'<path d="{d}" transform="{tr}"/>')
        ribs.append(f'<path d="M0,{n(-ln * .12)} Q{n(curl * .4)},{n(-ln * .55)} {n(curl * .85)},{n(-ln * .9)}" transform="{tr}"/>')
    cup = (f'<path d="M{n(x - L * .2)},{n(y + L * .05)} C{n(x - L * .2)},{n(y - L * .14)} {n(x + L * .2)},{n(y - L * .14)} '
           f'{n(x + L * .2)},{n(y + L * .05)}Z"/>')
    vol = spiral(x - L * .21, y + L * .03, L / 70, arcs=4) + " " + spiral(x + L * .21, y + L * .03, L / 70, mirror=True, arcs=4)
    return (f'<g fill="url(#gStoneLeaf)" stroke="#A8842F" stroke-width="{n(sw)}" stroke-linejoin="round">{"".join(leaves)}{cup}</g>'
            f'<g fill="none" stroke="#B59A63" stroke-width="{n(sw * .7)}" opacity=".85">{"".join(ribs)}</g>'
            f'<path d="{vol}" fill="none" stroke="#A8842F" stroke-width="{n(sw)}"/>')


def wreath(cx, cy, R, seed):
    rnd = random.Random(seed)
    lf = "M0,0 C3.2,-3 3.4,-9 0,-14 C-3.4,-9 -3.2,-3 0,0Z"
    stems, leaves, ribs, berries = [], [], [], []
    for s in (-1, 1):
        pts = []
        for i in range(31):
            th = math.radians(8 + i * 5)
            pts.append((cx + s * R * math.sin(th), cy + R * math.cos(th)))
        stems.append(smooth(pts))
        for i in range(2, 31, 2):
            th = math.radians(8 + i * 5)
            px, py = cx + s * R * math.sin(th), cy + R * math.cos(th)
            tx, ty = s * math.cos(th), -math.sin(th)
            base = math.degrees(math.atan2(tx, -ty))
            sc = 1 - .3 * i / 30
            for side in (-1, 1):
                a = base + side * 34 + rnd.uniform(-5, 5)
                tr = f"translate({n(px)} {n(py)}) rotate({n(a)}) scale({n(sc)})"
                leaves.append(f'<path d="{lf}" transform="{tr}"/>')
                ribs.append(f'<path d="M0,-1 L0,-12" transform="{tr}"/>')
            if i % 6 == 0:
                berries.append(f'<circle cx="{n(px - s * 3)}" cy="{n(py + 2)}" r="1.7"/>')
    body = (f'<g fill="none" stroke="#B3AB9C" stroke-width="1.6">{"".join(f"<path d=\"{d}\"/>" for d in stems)}</g>'
            f'<g fill="url(#gRelief)" stroke="#8F8778" stroke-opacity=".6" stroke-width=".6">{"".join(leaves)}{"".join(berries)}</g>'
            f'<g stroke="#A79F90" stroke-width=".5" opacity=".8">{"".join(ribs)}</g>')
    shadow = f'<g transform="translate(1.6 2.2)" filter="url(#fCast)">{body}</g>'
    by = cy + R + 1
    bow = (f'<g fill="url(#gGold)" stroke="#6E541A" stroke-width=".5">'
           f'<path d="M{n(cx)},{n(by)} C{n(cx - 9)},{n(by - 8)} {n(cx - 15)},{n(by + 2)} {n(cx - 4)},{n(by + 3)}Z"/>'
           f'<path d="M{n(cx)},{n(by)} C{n(cx + 9)},{n(by - 8)} {n(cx + 15)},{n(by + 2)} {n(cx + 4)},{n(by + 3)}Z"/>'
           f'<path d="M{n(cx - 2)},{n(by + 2)} L{n(cx - 10)},{n(by + 17)} L{n(cx - 7)},{n(by + 14)} L{n(cx - 5)},{n(by + 18)}Z"/>'
           f'<path d="M{n(cx + 2)},{n(by + 2)} L{n(cx + 10)},{n(by + 17)} L{n(cx + 7)},{n(by + 14)} L{n(cx + 5)},{n(by + 18)}Z"/>'
           f'<circle cx="{n(cx)}" cy="{n(by + 1)}" r="2.6"/></g>')
    return shadow + body + bow


def pediment():
    rnd = random.Random(21)
    o = []
    roof = lambda x: 8 + .2903 * abs(x - 558)
    tymp = "82,172 558,32 1034,172"
    o.append(f'<clipPath id="pedT"><polygon points="{tymp}"/></clipPath>')
    o.append(f'<polygon points="{tymp}" fill="url(#gTymp)"/>')
    o.append(f'<g clip-path="url(#pedT)"><polyline points="{tymp}" fill="none" stroke="#5E564A" stroke-opacity=".35" '
             f'stroke-width="10" filter="url(#fSoft)"/>')
    for x in (170, 250, 330, 450, 690, 800, 905, 985):
        y = 32 + .294 * abs(x - 558)
        o.append(f'<rect x="{x}" y="{n(y)}" width="{rnd.randint(5, 12)}" height="{rnd.randint(26, 60)}" fill="url(#gStreak)" filter="url(#fSoft)"/>')
    o.append('</g>')
    o.append(wreath(558, 112, 34, 5))
    o.append('<polygon points="0,172 558,8 1116,172 1034,172 558,32 82,172" fill="url(#gCorona)"/>')
    for off, col, w, op in ((1.2, "#fff", 1.6, 1), (5, "#D3CCBF", 4, 1), (8.4, "#fff", 1, .8), (14.5, "#F8F6F2", 8, 1),
                            (19.2, "#6F6657", 1.4, .45), (21, "#A8842F", .9, .6)):
        o.append(f'<polyline points="0,{n(170 + off)} 558,{n(8 + off)} 1116,{n(170 + off)}" fill="none" stroke="{col}" '
                 f'stroke-width="{w}" opacity="{op}" clip-path="url(#pedR)"/>')
    o.insert(0, '<clipPath id="pedR"><polygon points="0,172 558,8 1116,172 1034,172 558,32 82,172"/></clipPath>')
    o.append('<rect x="0" y="172" width="1116" height="18" fill="url(#gCorona)"/>')
    o.append('<path d="M0,172.7 H1116" stroke="#fff" stroke-width="1.4"/><path d="M0,189.4 H1116" stroke="#6F6657" stroke-opacity=".45" stroke-width="1.4"/>')
    o.append('<path d="M0,191.4 H1116" stroke="#A8842F" stroke-width="1.2" opacity=".7"/>')
    o.append('<rect x="0" y="193" width="1116" height="12" fill="#C9C1B3"/><rect x="0" y="193" width="1116" height="12" fill="url(#pDentil)"/>')
    o.append('<rect x="0" y="205" width="1116" height="9" fill="url(#gTorus)"/><path d="M0,213.4 H1116" stroke="#6F6657" stroke-opacity=".4"/>')
    sil = "M0,170 L558,8 L1116,170 L1116,214 L0,214Z"
    o.append(f'<path d="{sil}" fill="#fff" filter="url(#fVeinsBig)" opacity=".5"/>')
    o.append(f'<path d="{sil}" fill="#fff" filter="url(#fGrain)" opacity=".5"/>')
    o.append(f'<polyline points="0,170 558,8 1116,170" fill="none" stroke="#8F8778" stroke-opacity=".6"/>')
    # wear
    for x in (300, 742):
        y = roof(x)
        o.append(f'<path d="M{x - 9},{n(y - 1)} L{x + 8},{n(y + 1)} L{x + 5},{n(y + 6)} L{x - 3},{n(y + 5)}Z" fill="#F5F3EE"/>')
        o.append(f'<path d="M{x + 8},{n(y + 1)} L{x + 5},{n(y + 6)} L{x - 3},{n(y + 5)} L{x - 9},{n(y - 1)}" fill="none" stroke="#7C7465" stroke-width=".8"/>')
    for x in (40, 120, 980, 1080):
        o.append(moss(x, roof(x) + 3, 6, rnd, 8, .8))
    o.append(moss(30, 171, 12, rnd, 10))
    o.append(moss(1090, 171, 12, rnd, 10))
    o.append(palmette(558, 9, 50))
    o.append(palmette(12, 170, 34, side=-1, k=3))
    o.append(palmette(1104, 170, 34, side=1, k=3))
    return "".join(o)


def steps(widths, heights, seed, total_w):
    rnd = random.Random(seed)
    o = []
    y = 0
    outline = []
    for (x0, x1), h in zip(widths, heights):
        w = x1 - x0
        o.append(f'<rect x="{x0}" y="{y}" width="{w}" height="4" fill="#F6F4EF"/>')
        o.append(f'<rect x="{x0}" y="{y + 4}" width="{w}" height="{h - 4}" fill="url(#gRiser)"/>')
        o.append(f'<path d="M{x0},{y + .5} H{x1}" stroke="#fff" stroke-width="1"/><path d="M{x0},{y + 4.3} H{x1}" stroke="#6F6657" stroke-opacity=".35"/>')
        for _ in range(max(2, w // 160)):
            o.append(chip(rnd.uniform(x0 + 20, x1 - 20), y + 4, rnd.uniform(1.6, 3), rnd))
        o.append(moss(x0 + 6, y + h - 1, 5, rnd, 7))
        o.append(moss(x1 - 6, y + h - 1, 5, rnd, 7))
        outline.append((x0, x1, y, y + h))
        y += h
    d = "M" + " L".join(f"{x0},{t} {x1},{t}" for x0, x1, t, b in outline)
    o.append(f'<rect x="0" y="0" width="{total_w}" height="{y}" fill="#fff" filter="url(#fGrain)" opacity=".45" clip-path="url(#stepsClip{seed})"/>')
    clip = "".join(f'<rect x="{x0}" y="{t}" width="{x1 - x0}" height="{b - t}"/>' for x0, x1, t, b in outline)
    return f'<clipPath id="stepsClip{seed}">{clip}</clipPath>' + "".join(o)


def card_roof(seed):
    rnd = random.Random(seed)
    o = ['<clipPath id="roofR%d"><polygon points="0,58 185,6 370,58 329,58 185,16 41,58"/></clipPath>' % seed]
    o.append('<polygon points="41,58 185,16 329,58" fill="url(#gTymp)"/>')
    o.append('<polygon points="0,58 185,6 370,58 329,58 185,16 41,58" fill="url(#gCorona)"/>')
    for off, col, w, op in ((.8, "#fff", 1.1, 1), (3.4, "#D3CCBF", 2.6, 1), (7, "#F8F6F2", 4, 1), (9.4, "#6F6657", 1, .45), (10.4, "#A8842F", .7, .6)):
        o.append(f'<polyline points="0,{n(58 + off)} 185,{n(6 + off)} 370,{n(58 + off)}" fill="none" stroke="{col}" '
                 f'stroke-width="{w}" opacity="{op}" clip-path="url(#roofR{seed})"/>')
    o.append('<rect x="0" y="58" width="370" height="7" fill="url(#gCorona)"/><path d="M0,58.5 H370" stroke="#fff"/><path d="M0,64.5 H370" stroke="#6F6657" stroke-opacity=".45"/>')
    o.append('<path d="M0,65.6 H370" stroke="#A8842F" stroke-width=".8" opacity=".7"/>')
    o.append('<rect x="0" y="66.2" width="370" height="3.8" fill="#C9C1B3"/><rect x="0" y="66.2" width="370" height="3.8" fill="url(#pDentilS)"/>')
    o.append('<path d="M0,58 L185,6 L370,58 L370,70 L0,70Z" fill="#fff" filter="url(#fGrain)" opacity=".5"/>')
    o.append('<polyline points="0,58 185,6 370,58" fill="none" stroke="#8F8778" stroke-opacity=".6"/>')
    o.append(moss(30, 49, 7, rnd, 7, .8))
    o.append(moss(340, 49, 7, rnd, 7, .8))
    o.append(palmette(185, 7, 26, sw=.6))
    o.append(palmette(6, 58, 17, side=-1, k=3, sw=.5))
    o.append(palmette(364, 58, 17, side=1, k=3, sw=.5))
    return "".join(o)


def architrave(w, h):
    a, b = h * .32, h * .66
    return (f'<rect x="4" y="0" width="{w - 8}" height="{n(a)}" fill="#F3F0EA"/><rect x="6" y="{n(a)}" width="{w - 12}" height="{n(b - a)}" fill="#ECE7DF"/>'
            f'<rect x="8" y="{n(b)}" width="{w - 16}" height="{n(h - b)}" fill="#E3DDD2"/>'
            f'<path d="M4,.5 H{w - 4}" stroke="#fff"/><path d="M6,{n(a)} H{w - 6} M8,{n(b)} H{w - 8}" stroke="#6F6657" stroke-opacity=".3"/>'
            f'<path d="M8,{n(h - .5)} H{w - 8}" stroke="#6F6657" stroke-opacity=".45"/>'
            f'<rect x="4" y="0" width="{w - 8}" height="{h}" fill="#fff" filter="url(#fGrain)" opacity=".45"/>')


# ---------- defs ----------
def lin(id_, stops, x2=0, y2=1, x1=0, y1=0):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"{"" if a is None else f" stop-opacity=\"{a}\""}/>' for o, c, a in stops)
    return f'<linearGradient id="{id_}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rad(id_, stops, cx=.5, cy=.5, r=.5):
    s = "".join(f'<stop offset="{o}" stop-color="{c}"/>' for o, c in stops)
    return f'<radialGradient id="{id_}" cx="{cx}" cy="{cy}" r="{r}">{s}</radialGradient>'


def table(nv, peaks):
    v = [0.0] * nv
    for i, a in peaks:
        v[i] = a
    return " ".join(n(x) for x in v)


DEFS = "".join([
    lin("gShaft", [(0, "#C6BEB0", None), (.12, "#E4DFD6", None), (.3, "#FAF8F4", None), (.46, "#F3F0EA", None),
                   (.7, "#DCD6CB", None), (.9, "#C2BAAC", None), (1, "#A69E90", None)], x2=1, y2=0),
    lin("gFlute", [(0, "#544C40", .4), (.45, "#544C40", .1), (.8, "#FFFFFF", .5), (1, "#FFFFFF", .1)], x2=1, y2=0),
    lin("gSpec", [(0, "#FFFFFF", 0), (.5, "#FFFFFF", .45), (1, "#FFFFFF", 0)], x2=1, y2=0),
    lin("gStreak", [(0, "#64594A", .26), (1, "#64594A", 0)]),
    lin("gGrime", [(0, "#5E6F4E", 0), (1, "#5E6F4E", .3)]),
    lin("gTorus", [(0, "#FBFAF7", None), (.45, "#ECE8E0", None), (1, "#B5AD9E", None)]),
    lin("gScotia", [(0, "#A39B8C", None), (1, "#E6E1D8", None)]),
    lin("gPlinth", [(0, "#F1EEE8", None), (1, "#D0C9BC", None)]),
    lin("gCap", [(0, "#FCFBF8", None), (1, "#DAD4C9", None)]),
    lin("gEchinus", [(0, "#CFC8BB", None), (1, "#BEB6A7", None)]),
    lin("gRiser", [(0, "#E4DED3", None), (1, "#C8C0B2", None)]),
    lin("gGold", [(0, "#E6CC85", None), (.45, "#B8913A", None), (1, "#7F6220", None)], x2=1, y2=1),
    lin("gRelief", [(0, "#FFFFFF", None), (1, "#CEC7BA", None)], x2=1, y2=1),
    lin("gStoneLeaf", [(0, "#FFFFFF", None), (1, "#D6CFC2", None)], x2=1, y2=1),
    lin("gTymp", [(0, "#E2DCD1", None), (1, "#D7D0C3", None)]),
    lin("gCorona", [(0, "#FBFAF7", None), (1, "#E2DCD1", None)]),
    lin("gDentil", [(0, "#F8F6F2", None), (.7, "#E2DCD1", None), (1, "#C6BEB0", None)], x2=1, y2=0),
    rad("gEgg", [(0, "#FFFFFF"), (.6, "#EDE9E1"), (1, "#CCC5B8")], .4, .35, .7),
    rad("gBead", [(0, "#FFFFFF"), (1, "#CBC4B6")], .4, .35, .7),
    rad("gVolute", [(0, "#FFFFFF"), (.55, "#EBE6DE"), (1, "#BDB5A6")], .38, .32, .75),
    rad("lfA", [(0, "#7AA660"), (.55, "#4B7541"), (1, "#2C4926")], .5, .9, .95),
    rad("lfB", [(0, "#A8C886"), (.55, "#739A56"), (1, "#486C3A")], .5, .9, .95),
    rad("lfC", [(0, "#5C8749"), (.55, "#3A5E33"), (1, "#1F371B")], .5, .9, .95),
    rad("lfD", [(0, "#93B46E"), (.5, "#5E8449"), (1, "#395930")], .5, .9, .95),
    rad("lfBack", [(0, "#45623B"), (1, "#1E2F1A")], .5, .9, .95),
    '<pattern id="pDentil" width="14" height="12" patternUnits="userSpaceOnUse"><rect x="2" y="0" width="9" height="12" fill="url(#gDentil)"/>'
    '<rect x="11" y="0" width="1.4" height="12" fill="#5E564A" opacity=".25"/><path d="M2,.5 H11" stroke="#fff"/></pattern>',
    '<pattern id="pDentilS" width="7" height="3.8" patternUnits="userSpaceOnUse"><rect x="1" y="0" width="4.5" height="3.8" fill="url(#gDentil)"/></pattern>',
    '<pattern id="meander" width="20" height="14" patternUnits="userSpaceOnUse"><path d="M0,13 H20 M0,13 V1 H14 V9 H6 V5 H10" fill="none" stroke="#A8842F" stroke-width="1.3"/></pattern>',
    '<filter id="fGrain" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="3" seed="4" result="n"/>'
    '<feColorMatrix in="n" type="matrix" values="0 0 0 0 .34  0 0 0 0 .31  0 0 0 0 .26  3 0 0 0 -1.75" result="g"/>'
    '<feComposite in="g" in2="SourceGraphic" operator="in"/></filter>',
    '<filter id="fVeins" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency=".035 .009" numOctaves="4" seed="9" result="n"/>'
    '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="a"/>'
    f'<feComponentTransfer in="a" result="v"><feFuncA type="table" tableValues="{table(61, [(18, .15), (29, .2), (30, .7), (31, .2), (42, .15)])}"/></feComponentTransfer>'
    '<feFlood flood-color="#8E8677" result="c"/><feComposite in="c" in2="v" operator="in" result="cv"/>'
    '<feComposite in="cv" in2="SourceGraphic" operator="in"/></filter>',
    '<filter id="fVeinsBig" color-interpolation-filters="sRGB"><feTurbulence type="fractalNoise" baseFrequency=".0045 .0075" numOctaves="5" seed="3" result="n"/>'
    '<feColorMatrix in="n" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="a"/>'
    f'<feComponentTransfer in="a" result="v"><feFuncA type="table" tableValues="{table(101, [(49, .12), (50, .5), (51, .12)])}"/></feComponentTransfer>'
    '<feFlood flood-color="#ABA395" result="c"/><feComposite in="c" in2="v" operator="in" result="cv"/>'
    '<feComposite in="cv" in2="SourceGraphic" operator="in"/></filter>',
    '<filter id="fCast" x="-20%" y="-20%" width="140%" height="140%" color-interpolation-filters="sRGB">'
    '<feColorMatrix type="matrix" values="0 0 0 0 .16  0 0 0 0 .14  0 0 0 0 .1  0 0 0 .34 0"/><feGaussianBlur stdDeviation="1.5"/></filter>',
    '<filter id="fSoft" x="-30%" y="-10%" width="160%" height="120%"><feGaussianBlur stdDeviation="1.2"/></filter>',
    '<filter id="fMoss" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation=".8"/></filter>',
    f'<g id="leaf"><path d="M0,0 C.7,-3 .5,-6 0,-9" fill="none" stroke="#5B4730" stroke-width="1.4" stroke-linecap="round"/>'
    f'<g transform="translate(0 -9)"><path d="{LEAF}" stroke="#1C2F17" stroke-opacity=".55" stroke-width=".8" stroke-linejoin="round"/>'
    f'<path d="{SHEEN}" fill="#fff" opacity=".13"/><path d="{VEINS}" fill="none" stroke="currentColor" stroke-width="1" '
    f'stroke-linecap="round" opacity=".8"/></g></g>',
    '<g id="rosette">' + "".join(f'<ellipse cx="0" cy="-3.3" rx="1.7" ry="3" transform="rotate({k * 45})"/>' for k in range(8))
    .replace("<ellipse", '<ellipse fill="url(#gGold)" stroke="#6E541A" stroke-width=".3"') + '<circle r="1.7" fill="#7F6220"/></g>',
])


def sprig():
    lf = "M0,0 C2.6,-2.4 2.8,-7.5 0,-11.5 C-2.8,-7.5 -2.6,-2.4 0,0Z"
    pts = [(0, 0), (10, -2.5), (20, -6), (30, -11), (38, -17)]
    o = [f'<path d="{smooth(pts)}" fill="none" stroke="#7F6220" stroke-width="1.1"/>']
    for i, (x, y) in enumerate(pts[1:], 1):
        px, py = pts[i - 1]
        base = math.degrees(math.atan2(x - px, -(y - py)))
        for side in (-1, 1):
            o.append(f'<path d="{lf}" transform="translate({n(x)} {n(y)}) rotate({n(base + side * 38)}) scale({n(1 - i * .08)})" '
                     f'fill="url(#gGold)" stroke="#6E541A" stroke-width=".35"/>')
    o.append('<circle cx="16" cy="-1" r="1.6" fill="#7F6220"/><circle cx="27" cy="-5" r="1.4" fill="#7F6220"/>')
    return '<g id="sprig">' + "".join(o) + "</g>"


# ---------- assemble drawings ----------
cols = column("colHero", 60, 0, 705, 30, 3) + column("colHeroB", 60, 0, 705, 30, 8, broken=True)
cols += column("colCard", 30, 0, 425, 18, 5) + column("colCardB", 30, 0, 425, 18, 11, broken=True)

b1, f1 = helix(60, 30, 672, 52, 2.6, 1, .7, phase=-.4, per_turn=11, d0=.5, dur=2.6)
cb, cf = clump(60, 702, 46, 2, .7, d0=.25)
COL_OL = col_instance("colHero", b1 + cb, f1 + cf, "ivyOL", 3.2)
b2, f2 = helix(60, 30, 672, 380, 1.3, 3, .66, phase=1.3, per_turn=11, d0=.8, dur=1.6)
cb2, cf2 = clump(60, 703, 44, 4, .64, count=12, d0=.4)
COL_IL = col_instance("colHero", b2 + cb2, f2 + cf2, "ivyIL", 2.5)
cb3, cf3 = clump(60, 703, 40, 6, .58, count=6, d0=.6)
COL_IR = col_instance("colHeroB", cb3, cf3, "ivyIR", 1.4)
b4, f4 = helix(60, 30, 48, 360, 1.5, 7, .64, phase=.6, w0=2.2, w1=1, per_turn=11, d0=1.8, dur=1.5)
COL_OR = col_instance("colHero", b4, f4, "ivyOR", 3.4)

# hero drape over the pediment corner (px in the hero frame, 1116 wide)
HERO_BACK = strand([(800, 118), (820, 122), (860, 148), (905, 147), (950, 172), (995, 177), (1035, 196), (1066, 198)], 31, .48, w=2, back=True, up=True, d0=.4, dur=1.3)
HERO_BACK += strand([(905, 147), (930, 128), (952, 120)], 32, .42, w=1.4, back=True, up=True, d0=1.0, dur=.6)
front_pts = [(1066, 198), (1084, 208), (1096, 222), (1102, 240), (1100, 256), (1094, 272), (1090, 292), (1086, 310), (1080, 326), (1070, 334), (1056, 340)]
HERO_FRONT_INNER = strand(front_pts, 33, .5, w=2.4, d0=1.1, dur=.9) + pendant(1104, 236, 300, 34, .46, sway=7, count=10, drift=12, d0=1.5, dur=1.6, swing=7)
HERO_FRONT_INNER += pendant(1046, 250, 72, 35, .4, sway=4, count=4, w=1.2, d0=1.6, dur=.7, swing=5.5)
HERO_FRONT_INNER += strand([(1084, 208), (1072, 214), (1060, 216)], 36, .44, w=1.4, d0=1.3, dur=.5)
HERO_FRONT = f'<g class="ivy-sh" style="--d:3.2s"><use href="#heroDrape" transform="translate(4 5)" filter="url(#fCast)"/></g><g id="heroDrape">{HERO_FRONT_INNER}</g>'

# metrics plaque ivy (frame 240x260, plaque starts at x40 y46)
PLAQUE_BACK = strand([(0, 18), (24, 26), (52, 34), (80, 44), (104, 58)], 41, .46, w=2, up=True, d0=.3, dur=1.0)
PLAQUE_BACK += strand([(80, 190), (62, 204), (44, 218), (24, 234), (4, 250)], 42, .44, w=1.8, hang=True, d0=.6, dur=.9)
PLAQUE_FRONT_INNER = strand([(0, 96), (22, 103), (44, 98), (62, 90), (80, 86), (96, 90)], 43, .48, w=2, d0=.8, dur=.9)
PLAQUE_FRONT_INNER += pendant(50, 99, 48, 44, .38, sway=4, count=3, w=1.1, d0=1.2, dur=.5, swing=6)
PLAQUE_FRONT = f'<g class="ivy-sh" style="--d:1.8s"><use href="#plaqueIvy" transform="translate(3 4)" filter="url(#fCast)"/></g><g id="plaqueIvy">{PLAQUE_FRONT_INNER}</g>'

# temple cards
cb_a, cf_a = helix(30, 18, 400, 120, 1.6, 51, .5, phase=.2, w0=1.8, w1=.9, scale=.7, per_turn=11, d0=.9, dur=1.6)
cl_a, clf_a = clump(30, 420, 26, 52, .42, count=10, d0=.7)
CARD1_L = col_instance("colCard", cb_a + cl_a, cf_a + clf_a, "ivyC1", 2.6)
CARD1_R = col_instance("colCard", "", "", "ivyC1r")
CARD2_L = col_instance("colCard", "", "", "ivyC2l")
cl_b, clf_b = clump(30, 421, 24, 53, .4, count=6, d0=1.0)
CARD2_R = col_instance("colCardB", cl_b, clf_b, "ivyC2", 1.8)
CARD3_L = col_instance("colCard", "", "", "ivyC3l")
cb_c, cf_c = helix(30, 18, 40, 290, 1.4, 54, .48, phase=.9, w0=1.6, w1=.9, scale=.7, per_turn=11, d0=1.9, dur=1.4)
CARD3_R = col_instance("colCard", cb_c, cf_c, "ivyC3", 3.4)
CARD3_BACK = strand([(10, 40), (40, 54), (72, 54), (100, 72), (122, 72), (134, 80)], 55, .34, w=1.5, back=True, up=True, d0=.9, dur=.9)
c3f = strand([(134, 80), (142, 88), (147, 98), (145, 108), (138, 115), (124, 118), (110, 121)], 56, .36, w=1.6, d0=1.4, dur=.6)
c3f += pendant(148, 96, 150, 57, .32, sway=4, count=7, w=1.1, drift=6, d0=1.7, dur=1.1, swing=6.5)
CARD3_FRONT = f'<g class="ivy-sh" style="--d:2.9s"><use href="#card3Ivy" transform="translate(3 4)" filter="url(#fCast)"/></g><g id="card3Ivy">{c3f}</g>'


# gold motes drifting in the temple light
_r = random.Random(77)
DUST = "".join(
    f'<i style="--x:{_r.uniform(16, 84):.1f}%;--y:{_r.uniform(30, 88):.1f}%;--s:{_r.uniform(1.6, 3.4):.1f}px;'
    f'--dx:{_r.uniform(-30, 30):.0f}px;--dur:{_r.uniform(11, 19):.1f}s;--d:{_r.uniform(.8, 9):.1f}s"></i>'
    for _ in range(16))

DRAW = dict(
    DUST=DUST,
    DEFS=DEFS + cols + sprig(),
    PEDIMENT=pediment(),
    ARCH_HERO=architrave(1116, 22),
    STEPS_HERO=steps([(24, 1140), (12, 1152), (0, 1164)], [15, 15, 16], 1, 1164),
    COL_OL=COL_OL, COL_IL=COL_IL, COL_IR=COL_IR, COL_OR=COL_OR,
    HERO_BACK=HERO_BACK, HERO_FRONT=HERO_FRONT,
    PLAQUE_BACK=PLAQUE_BACK, PLAQUE_FRONT=PLAQUE_FRONT,
    ROOF1=card_roof(61), ROOF2=card_roof(62), ROOF3=card_roof(63),
    ARCH_CARD=architrave(370, 16),
    STEPS_CARD1=steps([(8, 362), (4, 366), (0, 370)], [10, 10, 10], 71, 370),
    STEPS_CARD2=steps([(8, 362), (4, 366), (0, 370)], [10, 10, 10], 72, 370),
    STEPS_CARD3=steps([(8, 362), (4, 366), (0, 370)], [10, 10, 10], 73, 370),
    CARD1_L=CARD1_L, CARD1_R=CARD1_R, CARD2_L=CARD2_L, CARD2_R=CARD2_R, CARD3_L=CARD3_L, CARD3_R=CARD3_R,
    CARD3_BACK=CARD3_BACK, CARD3_FRONT=CARD3_FRONT,
    CROWN=palmette(30, 40, 34, sw=.6),
)

if TS_MODE:
    # Sorted keys + json.dumps keep the output byte-stable across runs.
    names = sorted(DRAW)
    body = ",\n".join(f"  {k}: {json.dumps(DRAW[k], ensure_ascii=False)}" for k in names)
    out = (
        "// Generated by tools/gen.py, do not edit. Regenerate: python3 tools/gen.py --ts src/drawings/generated.ts\n"
        f"export type DrawingName = {' | '.join(json.dumps(k) for k in names)};\n"
        f"export const drawings: Record<DrawingName, string> = {{\n{body},\n}};\n"
    )
    with open(OUT, "w") as fh:
        fh.write(out)
    print(f"wrote {OUT}: {len(out) // 1024} KiB")
    sys.exit()

with open(sys.argv[2]) as fh:
    page = Template(fh.read()).safe_substitute(DRAW)
with open(OUT, "w") as fh:
    fh.write(page)
print(f"wrote {OUT}: {len(page) // 1024} KiB")
