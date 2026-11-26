# -*- coding: utf-8 -*-
"""Primitives de dessin (supersampling x2) et utilitaires d'animation."""
import math
from functools import lru_cache
import numpy as np
from PIL import Image, ImageDraw, ImageFont

W, H, S = 1920, 1080, 2

FONTS = {
    "black": "/usr/share/fonts/opentype/inter/InterDisplay-Black.otf",
    "xbold": "/usr/share/fonts/opentype/inter/InterDisplay-ExtraBold.otf",
    "bold": "/usr/share/fonts/opentype/inter/Inter-Bold.otf",
    "semi": "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf",
    "reg": "/usr/share/fonts/opentype/inter/Inter-Regular.otf",
    "med": "/usr/share/fonts/opentype/inter/Inter-Medium.otf",
    "mono": "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Bold.ttf",
    "serif": "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "serifr": "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
}

INK = (13, 16, 22)
WHITE = (243, 239, 230)
RED = (230, 57, 70)
AMBER = (244, 185, 66)
TEAL = (46, 196, 182)
BLUE = (77, 157, 224)
GREY = (138, 147, 163)
DGREY = (52, 58, 70)
PAPER = (236, 228, 210)
PAPERD = (205, 194, 170)
DARK = (27, 27, 27)


@lru_cache(maxsize=512)
def font(name, size):
    import os
    p = FONTS[name]
    if not os.path.exists(p):
        p = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if name == "mono" else \
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    return ImageFont.truetype(p, max(4, int(size * S)))


def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def eout(x):
    x = clamp(x); return 1 - (1 - x) ** 3


def einout(x):
    x = clamp(x); return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2


def eback(x):
    x = clamp(x); c1 = 1.9; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2


def lerp(a, b, x):
    return a + (b - a) * x


def mixc(c1, c2, x):
    return tuple(int(lerp(a, b, x)) for a, b in zip(c1, c2))


def _bg_gradient(top, bot, glow=None):
    y = np.linspace(0, 1, H * S)[:, None, None]
    arr = (np.array(top)[None, None] * (1 - y) + np.array(bot)[None, None] * y)
    arr = np.repeat(arr, W * S, axis=1)
    if glow:
        gx, gy, gr, gc, ga = glow
        yy, xx = np.mgrid[0:H * S, 0:W * S]
        d = np.sqrt((xx / S - gx) ** 2 + (yy / S - gy) ** 2) / gr
        g = np.clip(1 - d, 0, 1)[..., None] ** 2 * ga
        arr = arr * (1 - g) + np.array(gc)[None, None] * g
    return Image.fromarray(arr.astype(np.uint8))


BGS = {}


def get_bg(kind):
    if kind not in BGS:
        if kind == "dark":
            BGS[kind] = _bg_gradient((18, 22, 31), (8, 10, 14), (960, 380, 1100, (34, 42, 60), .6))
        elif kind == "red":
            BGS[kind] = _bg_gradient((60, 12, 18), (14, 4, 6), (960, 540, 1000, (120, 20, 30), .5))
        elif kind == "paper":
            BGS[kind] = _bg_gradient((238, 230, 212), (214, 203, 180), (960, 400, 1100, (246, 240, 226), .6))
        elif kind == "desk":
            BGS[kind] = _bg_gradient((58, 40, 28), (26, 17, 11), (960, 460, 900, (110, 78, 50), .55))
        elif kind == "teal":
            BGS[kind] = _bg_gradient((10, 40, 44), (5, 14, 16), (960, 420, 1000, (20, 80, 80), .5))
        elif kind == "amber":
            BGS[kind] = _bg_gradient((50, 36, 10), (14, 10, 4), (960, 420, 1000, (100, 70, 20), .5))
    return BGS[kind]


class R:
    """Canvas en coordonnées logiques 1920x1080, rendu interne x2."""

    def __init__(self, bg="dark"):
        self.im = get_bg(bg).copy()
        self.d = ImageDraw.Draw(self.im, "RGBA")
        self.cam = dict(z=1.0, ang=0.0, sx=0.0, sy=0.0, cx=960.0, cy=540.0, flash=0.0, rgb=0.0)

    # ---------------- bases
    @staticmethod
    def C(c, a=1.0):
        return (c[0], c[1], c[2], int(255 * clamp(a)))

    def text(self, x, y, s, f=("black", 80), fill=WHITE, a=1.0, anchor="mm", sc=1.0, stroke=0, sfill=INK):
        if a <= 0.01 or sc <= 0.02:
            return
        fo = font(f[0], f[1] * sc)
        if a >= 0.99:
            self.d.text((x * S, y * S), s, font=fo, fill=self.C(fill, 1), anchor=anchor,
                        stroke_width=int(stroke * S), stroke_fill=self.C(sfill, 1))
            return
        # PIL ne mélange pas l'alpha du texte : on passe par un masque
        x0, y0, x1, y1 = self.d.textbbox((x * S, y * S), s, font=fo, anchor=anchor)
        x0, y0 = int(x0) - 2, int(y0) - 2
        mw, mh = int(x1) - x0 + 4, int(y1) - y0 + 4
        if mw <= 0 or mh <= 0:
            return
        mask = Image.new("L", (mw, mh), 0)
        ImageDraw.Draw(mask).text((x * S - x0, y * S - y0), s, font=fo, fill=int(255 * a), anchor=anchor)
        self.im.paste(tuple(fill[:3]), (x0, y0), mask)

    def tw(self, s, f):
        return font(f[0], f[1]).getlength(s) / S

    def rect(self, x0, y0, x1, y1, fill=None, a=1.0, outline=None, w=0, r=0, oa=None):
        if a <= 0.01 and (oa is None or oa <= 0.01):
            return
        box = [x0 * S, y0 * S, x1 * S, y1 * S]
        if box[2] < box[0]: box[0], box[2] = box[2], box[0]
        if box[3] < box[1]: box[1], box[3] = box[3], box[1]
        kw = dict(fill=self.C(fill, a) if fill else None,
                  outline=self.C(outline, a if oa is None else oa) if outline else None, width=int(w * S))
        if r:
            self.d.rounded_rectangle(box, radius=r * S, **kw)
        else:
            self.d.rectangle(box, **kw)

    def circle(self, x, y, rad, fill=None, a=1.0, outline=None, w=0):
        if a <= 0.01 or rad <= 0:
            return
        self.d.ellipse([(x - rad) * S, (y - rad) * S, (x + rad) * S, (y + rad) * S],
                       fill=self.C(fill, a) if fill else None,
                       outline=self.C(outline, a) if outline else None, width=int(w * S))

    def ellipse(self, x0, y0, x1, y1, fill=None, a=1.0):
        self.d.ellipse([x0 * S, y0 * S, x1 * S, y1 * S], fill=self.C(fill, a))

    def line(self, pts, fill=WHITE, w=4, a=1.0):
        if a <= 0.01:
            return
        self.d.line([(x * S, y * S) for x, y in pts], fill=self.C(fill, a), width=int(w * S), joint="curve")
        for x, y in (pts[0], pts[-1]):
            self.circle(x, y, w / 2 - 0.2, fill, a)

    def poly(self, pts, fill=None, a=1.0, outline=None, w=0):
        if a <= 0.01:
            return
        self.d.polygon([(x * S, y * S) for x, y in pts], fill=self.C(fill, a) if fill else None,
                       outline=self.C(outline, a) if outline else None, width=int(w * S))

    def arrow(self, x0, y0, x1, y1, fill=WHITE, w=6, a=1.0, head=22, p=1.0):
        if p <= 0.01:
            return
        x1, y1 = lerp(x0, x1, p), lerp(y0, y1, p)
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * 0.8 * math.cos(ang), y1 - head * 0.8 * math.sin(ang)
        self.line([(x0, y0), (bx, by)], fill, w, a)
        pts = [(x1, y1),
               (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45)),
               (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))]
        self.poly(pts, fill, a)

    def paste_layer(self, layer, x, y, ang=0, sc=1.0, a=1.0):
        """layer : image RGBA déjà à l'échelle S."""
        if a <= 0.01 or sc <= 0.01:
            return
        L = layer
        if sc != 1.0:
            L = L.resize((max(1, int(L.width * sc)), max(1, int(L.height * sc))), Image.BILINEAR)
        if ang:
            L = L.rotate(ang, expand=True, resample=Image.BICUBIC)
        if a < 1:
            al = L.getchannel("A").point(lambda v: int(v * a))
            L = L.copy(); L.putalpha(al)
        self.im.paste(L, (int(x * S - L.width / 2), int(y * S - L.height / 2)), L)


# ---------------- couches réutilisables
@lru_cache(maxsize=64)
def stamp_layer(txt, color, size=90, pad=26):
    f = font("black", size)
    w = int(f.getlength(txt)) + pad * 2 * S
    h = int(size * S * 1.25) + pad * S
    L = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(L)
    d.rounded_rectangle([6 * S, 6 * S, w - 6 * S, h - 6 * S], radius=10 * S, outline=color + (235,), width=8 * S)
    d.text((w / 2, h / 2), txt, font=f, fill=color + (235,), anchor="mm")
    # texture usée
    rng = np.random.default_rng(len(txt))
    al = np.array(L.getchannel("A")).astype(np.float32)
    al *= (rng.random(al.shape) > 0.12)
    L.putalpha(Image.fromarray(al.astype(np.uint8)))
    return L


def stamp(r, txt, x, y, t, t0, color=RED, size=90, ang=-12):
    p = prog(t, t0, t0 + 0.18)
    if p <= 0:
        return
    sc = lerp(2.6, 1.0, eout(p))
    r.paste_layer(stamp_layer(txt, color, size), x, y, ang, sc, a=p)
    if 0 < t - t0 < 0.25:
        k = 1 - (t - t0) / 0.25
        r.cam["sx"] += math.sin(t * 90) * 10 * k
        r.cam["sy"] += math.cos(t * 77) * 8 * k


# ---------------- illustrations
def newspaper(r, x, y, w, h, mast, headline, a=1.0, grey=False, lines=True, sub=None):
    paper = (226, 226, 220) if grey else (244, 240, 230)
    r.rect(x + 10, y + 12, x + w + 10, y + h + 12, (0, 0, 0), a * 0.35, r=6)
    r.rect(x, y, x + w, y + h, paper, a, r=6)
    ink = (120, 120, 120) if grey else DARK
    r.text(x + w / 2, y + h * 0.10, mast, ("serif", w * 0.085), ink, a)
    r.rect(x + w * 0.06, y + h * 0.17, x + w * 0.94, y + h * 0.175, ink, a)
    r.rect(x + w * 0.06, y + h * 0.185, x + w * 0.94, y + h * 0.19, ink, a)
    if headline:
        r.text(x + w / 2, y + h * 0.27, headline, ("serif", w * 0.07), ink, a)
    if sub:
        r.text(x + w / 2, y + h * 0.345, sub, ("serifr", w * 0.04), ink, a)
    if lines:
        cols = 3
        cw = (w * 0.88) / cols
        for c in range(cols):
            cx = x + w * 0.06 + c * cw
            for k in range(11):
                yy = y + h * 0.40 + k * h * 0.05
                ll = cw * (0.86 if (k + c) % 4 else 0.6)
                r.rect(cx + 6, yy, cx + ll, yy + h * 0.018, (150, 150, 150) if grey else (90, 90, 90), a * 0.8)


def doc_sheet(r, x, y, w, h, ang=0, a=1.0, title=None):
    r.rect(x, y, x + w, y + h, PAPER, a, outline=PAPERD, w=2, r=3)
    for k in range(9):
        yy = y + h * 0.2 + k * h * 0.08
        r.rect(x + w * 0.1, yy, x + w * (0.9 if k % 3 else 0.6), yy + h * 0.025, (140, 130, 110), a)
    if title:
        r.text(x + w / 2, y + h * 0.1, title, ("mono", w * 0.07), DARK, a)


def person(r, x, y, sc=1.0, fill=GREY, a=1.0):
    r.circle(x, y - 70 * sc, 42 * sc, fill, a)
    r.d.chord([(x - 85 * sc) * S, (y - 10 * sc) * S, (x + 85 * sc) * S, (y + 160 * sc) * S], 180, 360,
              fill=R.C(fill, a))


def pentagon_pts(cx, cy, rad, rot=-90):
    return [(cx + rad * math.cos(math.radians(rot + 72 * i)), cy + rad * math.sin(math.radians(rot + 72 * i)))
            for i in range(5)]


def court(r, cx, cy, sc=1.0, a=1.0, col=WHITE):
    w = 560 * sc
    r.poly([(cx - w / 2 - 20 * sc, cy - 150 * sc), (cx + w / 2 + 20 * sc, cy - 150 * sc), (cx, cy - 260 * sc)],
           col, a)
    r.rect(cx - w / 2 - 20 * sc, cy - 150 * sc, cx + w / 2 + 20 * sc, cy - 125 * sc, col, a)
    for i in range(8):
        xx = cx - w / 2 + 20 * sc + i * (w - 40 * sc) / 7
        r.rect(xx - 16 * sc, cy - 120 * sc, xx + 16 * sc, cy + 110 * sc, col, a)
    for k in range(3):
        r.rect(cx - w / 2 - 20 * sc - k * 20 * sc, cy + 115 * sc + k * 22 * sc,
               cx + w / 2 + 20 * sc + k * 20 * sc, cy + 133 * sc + k * 22 * sc, col, a)


def rpoly(cx, cy, w, h, ang):
    c, s = math.cos(ang), math.sin(ang)
    pts = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    return [(cx + px * c - py * s, cy + px * s + py * c) for px, py in pts]


def gavel(r, x, y, ang, sc=1.0, col=AMBER, a=1.0):
    """Marteau qui pivote autour de (x, y) (bout du manche)."""
    L = 260 * sc
    hx, hy = x + L * math.cos(ang), y + L * math.sin(ang)
    r.poly(rpoly((x + hx) / 2, (y + hy) / 2, L, 22 * sc, ang), (150, 100, 50), a)
    r.poly(rpoly(hx, hy, 70 * sc, 150 * sc, ang), col, a)


def balance(r, cx, cy, tilt, ltxt, rtxt, lcol=RED, rcol=TEAL, a=1.0, sc=1.0):
    r.rect(cx - 8 * sc, cy, cx + 8 * sc, cy + 300 * sc, WHITE, a)
    r.rect(cx - 90 * sc, cy + 300 * sc, cx + 90 * sc, cy + 318 * sc, WHITE, a)
    bw = 340 * sc
    lx, ly = cx - bw * math.cos(tilt), cy - bw * math.sin(tilt)
    rx, ry = cx + bw * math.cos(tilt), cy + bw * math.sin(tilt)
    r.line([(lx, ly), (rx, ry)], WHITE, 12 * sc, a)
    r.circle(cx, cy, 16 * sc, WHITE, a)
    for px, py, txt, c in ((lx, ly, ltxt, lcol), (rx, ry, rtxt, rcol)):
        r.line([(px, py), (px - 60 * sc, py + 120 * sc)], GREY, 3, a)
        r.line([(px, py), (px + 60 * sc, py + 120 * sc)], GREY, 3, a)
        r.d.chord([(px - 120 * sc) * S, (py + 60 * sc) * S, (px + 120 * sc) * S, (py + 180 * sc) * S], 0, 180,
                  fill=R.C(c, a))
        r.text(px, py + 215 * sc, txt, ("bold", 34 * sc), c, a)


def star_pts(cx, cy, ro, ri, n=5):
    pts = []
    for i in range(2 * n):
        rr = ro if i % 2 == 0 else ri
        an = -math.pi / 2 + i * math.pi / n
        pts.append((cx + rr * math.cos(an), cy + rr * math.sin(an)))
    return pts


def coins(r, cx, cy, n, a=1.0, sc=1.0):
    for k in range(n):
        yy = cy - k * 22 * sc
        r.ellipse(cx - 70 * sc, yy - 18 * sc, cx + 70 * sc, yy + 18 * sc, (160, 110, 30), a)
        r.ellipse(cx - 70 * sc, yy - 26 * sc, cx + 70 * sc, yy + 10 * sc, AMBER, a)


def checkmark(r, x, y, sz, col=TEAL, a=1.0, p=1.0):
    pts = [(x - sz * 0.5, y), (x - sz * 0.12, y + sz * 0.38), (x + sz * 0.55, y - sz * 0.45)]
    if p < 0.5:
        q = p / 0.5
        r.line([pts[0], (lerp(pts[0][0], pts[1][0], q), lerp(pts[0][1], pts[1][1], q))], col, sz * 0.16, a)
    else:
        q = (p - 0.5) / 0.5
        r.line([pts[0], pts[1], (lerp(pts[1][0], pts[2][0], q), lerp(pts[1][1], pts[2][1], q))], col, sz * 0.16, a)


def cross(r, x, y, sz, col=RED, a=1.0):
    r.line([(x - sz / 2, y - sz / 2), (x + sz / 2, y + sz / 2)], col, sz * 0.16, a)
    r.line([(x + sz / 2, y - sz / 2), (x - sz / 2, y + sz / 2)], col, sz * 0.16, a)


def chip(r, x, y, txt, col=AMBER, a=1.0, size=34, txtcol=INK, anchor="m"):
    w = r.tw(txt, ("bold", size)) + size * 1.2
    h = size * 1.7
    x0 = x - w / 2 if anchor == "m" else x
    r.rect(x0, y - h / 2, x0 + w, y + h / 2, col, a, r=h / 2)
    r.text(x0 + w / 2, y + 1, txt, ("bold", size), txtcol, a)
    return w


def calendar(r, cx, cy, day, month, year, t, t0=0.0, sc=1.0):
    p = eback(prog(t, t0, t0 + 0.5))
    if p <= 0:
        return
    w, h = 420 * sc * p, 460 * sc * p
    r.rect(cx - w / 2 + 12, cy - h / 2 + 14, cx + w / 2 + 12, cy + h / 2 + 14, (0, 0, 0), .4, r=24 * sc)
    r.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2, WHITE, 1, r=24 * sc)
    r.rect(cx - w / 2, cy - h / 2, cx + w / 2, cy - h / 2 + 120 * sc * p, RED, 1, r=24 * sc)
    r.rect(cx - w / 2, cy - h / 2 + 90 * sc * p, cx + w / 2, cy - h / 2 + 120 * sc * p, RED, 1)
    r.text(cx, cy - h / 2 + 62 * sc * p, month.upper(), ("black", 60 * sc * p), WHITE)
    r.text(cx, cy + 40 * sc * p, str(day), ("black", 210 * sc * p), INK)
    r.text(cx, cy + 175 * sc * p, str(year), ("bold", 44 * sc * p), GREY)


def dust(r, t, n=40, col=WHITE, a=0.10, seed=3):
    rng = np.random.default_rng(seed)
    xs = rng.uniform(0, W, n); ys = rng.uniform(0, H, n)
    sp = rng.uniform(6, 22, n); sz = rng.uniform(1.5, 4, n); ph = rng.uniform(0, 6, n)
    for i in range(n):
        x = (xs[i] + t * sp[i]) % W
        y = (ys[i] - t * sp[i] * 0.5 + 8 * math.sin(t * .7 + ph[i])) % H
        r.circle(x, y, sz[i], col, a * (0.5 + 0.5 * math.sin(t + ph[i])))


def title_lines(r, t, t0, lines, x, y, f=("black", 110), col=WHITE, gap=1.15, stagger=0.12, anchor="mm",
                cols=None):
    for i, s in enumerate(lines):
        p = eout(prog(t, t0 + i * stagger, t0 + i * stagger + 0.4))
        c = cols[i] if cols else col
        r.text(x, y + i * f[1] * gap + (1 - p) * 40, s, f, c, p, anchor=anchor)


def typewriter(r, t, t0, s, x, y, f=("mono", 60), col=WHITE, cps=22, anchor="lm", cursor=True):
    n = int(max(0, t - t0) * cps)
    shown = s[:n]
    r.text(x, y, shown, f, col, 1, anchor=anchor)
    if cursor and n <= len(s) and int(t * 2.5) % 2 == 0:
        xx = x + r.tw(shown, f) if anchor == "lm" else x
        r.rect(xx + 6, y - f[1] * .45, xx + 6 + f[1] * .5, y + f[1] * .45, col, .9)
