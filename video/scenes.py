# -*- coding: utf-8 -*-
"""Une fonction par scène : f(r, t, d, m) — t temps local, d durée, m = [(début, durée)] des répliques."""
import math
from gfx import *

SCENES = {}


def scene(name, bg="dark"):
    def deco(f):
        SCENES[name] = (f, bg)
        return f
    return deco


def M(m, i):
    """début de la réplique i de la scène (ou fin si absente)."""
    return m[i][0] if i < len(m) else m[-1][0] + m[-1][1]


def frac(m, i, f):
    """instant à f (0..1) de la réplique i."""
    return m[i][0] + m[i][1] * f


def kb(r, t, d, z0=1.0, z1=1.06, cx=960, cy=540):
    """Ken Burns + punch-in d'entrée."""
    r.cam["z"] = lerp(z0, z1, t / max(d, .1)) + 0.07 * (1 - eout(prog(t, 0, .35)))
    r.cam["cx"], r.cam["cy"] = cx, cy


# ======================================================== 1. ACCROCHE
@scene("title_mars")
def s_title(r, t, d, m):
    kb(r, t, d, 1.0, 1.08)
    dust(r, t, 60)
    s = "MARS 1971"
    n = int(prog(t, 0.0, 0.8) * len(s) + 0.999)
    r.text(960, 500, s[:n], ("black", 250), WHITE)
    w = r.tw("MARS 1971", ("black", 250))
    p = eout(prog(t, 0.9, 1.6))
    r.rect(960 - w / 2, 640, 960 - w / 2 + w * p, 652, RED)
    r.text(960, 720, "ÉTATS-UNIS  ·  GUERRE DU VIETNAM", ("semi", 40), GREY, eout(prog(t, 1.2, 1.8)))


@scene("nyt_desk", "desk")
def s_nyt(r, t, d, m):
    kb(r, t, d, 1.0, 1.07, 960, 480)
    # bureau
    r.rect(0, 760, 1920, 1080, (40, 27, 18), 1)
    r.rect(0, 752, 1920, 768, (90, 62, 40), 1)
    p = eout(prog(t, 0, .7))
    newspaper(r, 560, 160 + (1 - p) * 500, 800, 620, "The New York Times", "ÉDITION DU JOUR", p)
    chip(r, 960, 110, "VOUS = LE DIRECTEUR", AMBER, eout(prog(t, frac(m, 0, .15), frac(m, 0, .3))), 36)
    q = eout(prog(t, frac(m, 0, .5), frac(m, 0, .7)))
    r.rect(330, 850, 1590, 935, INK, q * .85, r=18)
    r.text(960, 892, "L'UN DES PLUS GRANDS JOURNAUX DES ÉTATS-UNIS", ("xbold", 44), WHITE, q)


@scene("pages")
def s_pages(r, t, d, m):
    kb(r, t, d, 1.02, 1.1, 960, 520)
    dust(r, t)
    n = int(lerp(0, 7000, eout(prog(t, .2, d * .7))))
    nsheets = 1 + int(eout(prog(t, .2, d * .7)) * 22)
    for k in range(nsheets):
        yy = 800 - k * 16
        off = (k * 37) % 13 - 6
        r.rect(300 + off, yy - 16, 740 + off, yy, PAPER, 1, outline=PAPERD, w=2)
    top = 800 - nsheets * 16
    r.poly([(300, top), (740, top), (700, top - 260), (340, top - 260)], PAPER, 1, outline=PAPERD, w=2)
    r.text(520, top - 150, "TOP SECRET", ("mono", 34), RED)
    r.text(1250, 420, f"{n:,}".replace(",", " "), ("black", 230), WHITE)
    r.text(1250, 580, "PAGES", ("black", 90), AMBER)
    stamp(r, "TOP SECRET", 1250, 760, t, d * 0.62, RED, 80, -8)


@scene("pentagon")
def s_pentagon(r, t, d, m):
    kb(r, t, d, 1.0, 1.08, 760, 480)
    pts = pentagon_pts(600, 470, 300, -90)
    pts2 = pentagon_pts(600, 470, 180, -90)
    p = prog(t, 0, 1.4)
    seg = p * 5
    for i in range(5):
        q = clamp(seg - i)
        if q <= 0: break
        a, b = pts[i], pts[(i + 1) % 5]
        r.line([a, (lerp(a[0], b[0], q), lerp(a[1], b[1], q))], WHITE, 10)
        a, b = pts2[i], pts2[(i + 1) % 5]
        r.line([a, (lerp(a[0], b[0], q), lerp(a[1], b[1], q))], GREY, 6)
    if p >= 1:
        r.poly(pts, (255, 255, 255), .05)
    title_lines(r, t, .5, ["LE PENTAGONE"], 1000, 380, ("black", 110), WHITE, anchor="lm")
    title_lines(r, t, 1.0, ["= ministère de la Défense américain"], 1000, 470, ("semi", 44), GREY, anchor="lm")
    q = eout(prog(t, frac(m, 0, .7), frac(m, 0, .8)))
    if q > 0:
        chip(r, 1000, 600, "SUJET : LA GUERRE DU VIETNAM", RED, q, 40, WHITE, anchor="l")


@scene("ellsberg")
def s_ellsberg(r, t, d, m):
    kb(r, t, d, 1.0, 1.06)
    person(r, 560, 520, 1.6, (70, 78, 94))
    # documents qui s'échappent
    for k in range(9):
        tk = t - k * 0.25
        if tk < 0: continue
        x = 700 + tk * 420 + k * 10
        y = 430 + math.sin(tk * 3 + k) * 60 - k * 12
        r.paste_layer(sheet_layer(), x, y, ang=(k * 37 + tk * 60) % 360, sc=1.0, a=clamp(1.6 - tk * .45))
    p = eout(prog(t, .3, .8))
    r.rect(120, 740, 120 + 860 * p, 880, INK, .9, r=8)
    r.rect(120, 740, 132, 880, RED, p)
    r.text(160, 790, "DANIEL ELLSBERG", ("black", 64), WHITE, p, anchor="lm")
    r.text(160, 850, "ancien analyste militaire", ("med", 36), GREY, p, anchor="lm")
    q = eout(prog(t, frac(m, 0, .65), frac(m, 0, .75)))
    r.text(1500, 300, "FUITE", ("black", 150), RED, q)


_SHEET = None


def sheet_layer():
    global _SHEET
    if _SHEET is None:
        from PIL import Image as _I
        L = _I.new("RGBA", (120 * S, 160 * S), (0, 0, 0, 0))
        rr = R.__new__(R); rr.im = L; rr.d = ImageDraw.Draw(L, "RGBA"); rr.cam = {}
        doc_sheet(rr, 2, 2, 116, 156)
        _SHEET = L
    return _SHEET


@scene("explosif", "red")
def s_explosif(r, t, d, m):
    r.cam["z"] = 1.0 + 0.15 * (1 - eout(prog(t, 0, .4))) + 0.03 * t / d
    k = max(0, 1 - t / 0.6)
    r.cam["sx"] += math.sin(t * 80) * 16 * k
    r.cam["sy"] += math.cos(t * 67) * 12 * k
    r.cam["flash"] = max(0, 1 - t / 0.25) * .7
    p = eback(prog(t, .05, .4))
    r.text(960, 470, "EXPLOSIF", ("black", 260 * max(.01, p)), WHITE, 1, stroke=0)
    r.text(960, 680, "ce que le document révèle", ("semi", 46), (255, 200, 200), eout(prog(t, .5, 1)))


@scene("verite")
def s_verite(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    r.rect(360, 140, 1560, 820, PAPER, 1, r=6)
    r.text(960, 210, "UNITED STATES – VIETNAM RELATIONS, 1945–1967", ("mono", 32), DARK)
    lines = ["PENDANT DES ANNÉES,", "LE GOUVERNEMENT", "A CACHÉ LA VÉRITÉ", "AUX AMÉRICAINS."]
    for i, s in enumerate(lines):
        y = 340 + i * 110
        col = RED if i == 2 else DARK
        r.text(960, y, s, ("black", 78), col)
        # barres de censure qui s'effacent
        p = eout(prog(t, .4 + i * (d * .14), .9 + i * (d * .14)))
        w = 1060 * (1 - p)
        r.rect(960 - 530 + 1060 * p, y - 46, 960 + 530, y + 46, (12, 12, 12), 1 if w > 1 else 0)
    p = eout(prog(t, d * .7, d * .8))
    r.text(960, 890, "1945  ───────────  1967", ("mono", 40), WHITE, p)


@scene("dilemma")
def s_dilemma(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    p = eout(prog(t, 0, .5))
    r.text(960, 140, "VOUS FAITES QUOI ?", ("black", 96), WHITE, p)
    hl = 0 if t < M(m, 1) else (1 if t < M(m, 2) else 2)
    for side, (x, title, col, cons) in enumerate(((520, "PUBLIER", TEAL, "→ PROCÈS POSSIBLE"),
                                                  (1400, "SE TAIRE", GREY, "→ SCOOP PERDU"))):
        q = eback(prog(t, .3 + side * .15, .8 + side * .15))
        act = (hl == side + 1)
        dim = 1 if hl in (0, side + 1) else .35
        sc = 1.08 if act else 1.0
        w, h = 680 * sc * q, 420 * sc * q
        r.rect(x - w / 2, 520 - h / 2, x + w / 2, 520 + h / 2, col, .18 * dim, outline=col, w=5, oa=dim, r=28)
        r.text(x, 470, title, ("black", 110 * sc * max(q, .01)), WHITE, dim)
        if act:
            ta = M(m, side + 1)
            r.text(x, 600, cons, ("xbold", 48), RED if side == 0 else AMBER, eout(prog(t, ta + .6, ta + 1.1)))
            if side == 0:
                gavel(r, x + 220, 360, lerp(-1.6, -.5, eout(prog(t, ta + .8, ta + 1.2))), .6, AMBER)
    r.text(960, 520, "ou", ("semi", 50), GREY, eout(prog(t, .8, 1.1)))


@scene("cal13")
def s_cal13(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    calendar(r, 520, 480, 13, "juin", 1971, t, 0)
    p = eout(prog(t, .5, 1.1))
    newspaper(r, 900, 140 + (1 - p) * 700, 760, 640, "The New York Times", "PUBLIÉ", p,
              sub="Les documents du Pentagone")
    stamp(r, "PUBLIÉ", 1280, 700, t, d * .55, TEAL, 70, -10)


@scene("bascule", "red")
def s_bascule(r, t, d, m):
    r.cam["ang"] = -9 * eback(prog(t, 0, .6))
    r.cam["z"] = 1.12
    p = eout(prog(t, 0, .4))
    r.text(960, 470, "TOUT", ("black", 200), WHITE, p)
    r.text(960, 660, "BASCULE", ("black", 200), WHITE, eout(prog(t, .2, .6)))


@scene("ultimatum")
def s_ultimatum(r, t, d, m):
    kb(r, t, d, 1.0, 1.06)
    chip(r, 960, 90, "LE LENDEMAIN · 14 JUIN 1971", WHITE, eout(prog(t, 0, .4)), 32)
    person(r, 420, 560, 1.7, (92, 54, 60))
    p = eout(prog(t, .3, .8))
    r.rect(140, 780, 140 + 620 * p, 900, INK, .9, r=8)
    r.text(170, 820, "MINISTRE DE LA JUSTICE", ("black", 40), WHITE, p, anchor="lm")
    r.text(170, 868, "gouvernement du président Nixon", ("med", 30), GREY, p, anchor="lm")
    q = eback(prog(t, frac(m, 0, .45), frac(m, 0, .55)))
    if q > 0:
        r.rect(820, 230, 820 + 900 * q, 470, WHITE, 1, r=36)
        r.poly([(840, 420), (760, 520), (900, 450)], WHITE, q)
        r.text(1270, 350, "« ARRÊTEZ DE PUBLIER. »", ("black", 64 * q), INK)
    q2 = eback(prog(t, frac(m, 0, .82), frac(m, 0, .9)))
    if q2 > 0:
        r.text(1270, 640, "SINON : PROCÈS", ("black", 100 * q2), RED)
        if q2 > .9 and t - frac(m, 0, .9) < .3:
            r.cam["sx"] += math.sin(t * 90) * 8


@scene("refuse", "dark")
def s_refuse(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    newspaper(r, 200, 200, 560, 460, "The New York Times", "", 1, lines=True)
    p = eback(prog(t, 0, .35))
    r.text(1300, 430, "NON.", ("black", 300 * max(p, .01)), WHITE)
    r.text(1300, 640, "LE TIMES REFUSE", ("xbold", 64), AMBER, eout(prog(t, .3, .7)))


@scene("bloque")
def s_bloque(r, t, d, m):
    kb(r, t, d, 1.0, 1.06)
    newspaper(r, 560, 120, 800, 640, "The New York Times", "", 1, grey=True)
    gavel(r, 1600, 700, lerp(-2.2, -2.9, eout(prog(t, 0, .25))), 1.0, AMBER)
    stamp(r, "BLOQUÉ", 960, 450, t, .25, RED, 130, -14)
    q = eout(prog(t, .6, 1.0))
    r.rect(560, 830, 1360, 920, INK, q * .9, r=14)
    r.text(960, 875, "UN JUGE BLOQUE LA PUBLICATION", ("xbold", 42), WHITE, q)


@scene("fou")
def s_fou(r, t, d, m):
    r.cam["z"] = 1.0 + .03 * t
    g = 1 if (int(t * 12) % 5 == 0) else 0
    r.cam["rgb"] = 12 if g or t < .3 else 3
    r.cam["sx"] += (math.sin(t * 50) * 14) if g else 0
    title_lines(r, t, 0, ["MAIS VOILÀ", "OÙ ÇA DEVIENT"], 960, 340, ("black", 120), WHITE, stagger=.1)
    p = eback(prog(t, .45, .8))
    r.text(960, 700, "FOU", ("black", 260 * max(p, .01)), AMBER)


@scene("post")
def s_post(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    newspaper(r, 160, 200, 620, 520, "The New York Times", "", 1, grey=True)
    stamp(r, "BLOQUÉ", 470, 470, t, -1, RED, 70, -14)
    p = eout(prog(t, .2, .8))
    newspaper(r, 1140, 200 + (1 - p) * 600, 620, 520, "The Washington Post", "", p)
    q = eout(prog(t, frac(m, 0, .3), frac(m, 0, .4)))
    chip(r, 1450, 140, "LE CONCURRENT", BLUE, q, 34, WHITE)
    a = eout(prog(t, frac(m, 0, .6), frac(m, 0, .8)))
    doc_sheet(r, 880, 360, 160, 210, a=a, title="TOP SECRET")
    r.arrow(1050, 470, 1130, 470, AMBER, 8, a, p=a)
    r.text(960, 640, "MÊMES DOCUMENTS", ("black", 44), AMBER, a)


@scene("post_risk")
def s_post_risk(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    newspaper(r, 200, 200, 600, 520, "The Washington Post", "", 1)
    items = [("Il a vu ce qui est arrivé au Times", frac(m, 0, .05)), ("Il connaît le risque", frac(m, 0, .55))]
    for i, (s, ta) in enumerate(items):
        p = eout(prog(t, ta, ta + .4))
        y = 360 + i * 170
        r.rect(900, y - 60, 1780, y + 60, WHITE, .08 * p, r=20)
        checkmark(r, 960, y, 60, AMBER, p, prog(t, ta, ta + .5))
        r.text(1030, y, s, ("bold", 46), WHITE, p, anchor="lm")


@scene("cal18")
def s_cal18(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    calendar(r, 520, 480, 18, "juin", 1971, t, 0)
    p = eout(prog(t, .3, .9))
    newspaper(r, 900, 140 + (1 - p) * 700, 760, 640, "The Washington Post", "PUBLIÉ", p,
              sub="Les documents du Pentagone")
    stamp(r, "QUAND MÊME", 1280, 700, t, d * .35, TEAL, 66, -10)


@scene("pourquoi")
def s_pourquoi(r, t, d, m):
    st = M(m, 0)
    r.cam["z"] = 1.0 + .08 * prog(t, st, d)
    if t < st:
        return
    p = eback(prog(t, st, st + .4))
    r.text(960, 520, "POURQUOI ?", ("black", 240 * max(p, .01)), AMBER)


# ======================================================== chapitres
def chapter(r, t, d, num, title, sub):
    kb(r, t, d, 1.0, 1.04)
    p = eout(prog(t, 0, .5))
    r.text(560 - 40, 450, num, ("black", 420), (255, 255, 255), .07 * p, anchor="rm")
    r.rect(560, 300, 572, 300 + 300 * p, AMBER)
    title_lines(r, t, .15, [title], 620, 400, ("black", 110), WHITE, anchor="lm")
    title_lines(r, t, .4, [sub], 620, 520, ("semi", 48), AMBER, anchor="lm")
    for i in range(4):
        on = i < int(num)
        r.rect(620 + i * 130, 600, 620 + i * 130 + 110, 610, AMBER if on else DGREY, p)


@scene("chap2")
def s_chap2(r, t, d, m):
    chapter(r, t, d, "2", "LES QUESTIONS", "2 questions · 1 méthode")


@scene("chap3")
def s_chap3(r, t, d, m):
    chapter(r, t, d, "3", "LA RÉSOLUTION", "un exemple simple")


@scene("chap4")
def s_chap4(r, t, d, m):
    chapter(r, t, d, "4", "CE QU'ON RETIENT", "3 résultats")


def qcard(r, t, d, n, l1, l2, l3, col):
    kb(r, t, d, 1.0, 1.05)
    p = eback(prog(t, 0, .45))
    r.circle(330, 500, 150 * p, col, 1)
    r.text(330, 500, f"?{n}", ("black", 140 * max(p, .01)), INK)
    title_lines(r, t, .2, [l1, l2, l3], 560, 380, ("black", 84), WHITE, gap=1.2, anchor="lm",
                cols=[WHITE, col, WHITE])


@scene("q1")
def s_q1(r, t, d, m):
    qcard(r, t, d, 1, "Pourquoi un journal", "prend le risque", "d'un procès ?", AMBER)


@scene("q2")
def s_q2(r, t, d, m):
    qcard(r, t, d, 2, "Pourquoi un gouvernement", "lance un procès", "qu'il peut perdre ?", RED)


@scene("breakdown", "amber")
def s_breakdown(r, t, d, m):
    r.cam["z"] = 1.05
    r.cam["rgb"] = 10 if t < .25 or int(t * 10) % 7 == 0 else 2
    s = "LET'S BREAK IT DOWN"
    f = ("black", 130)
    tot = r.tw(s, f)
    x = 960 - tot / 2
    burst = eout(prog(t, d * .55, d))
    for i, ch in enumerate(s):
        w = r.tw(ch, f)
        ang = i * 2.39
        dx = math.cos(ang) * 500 * burst
        dy = math.sin(ang) * 300 * burst
        p = eout(prog(t, i * .02, i * .02 + .25))
        r.text(x + w / 2 + dx, 540 + dy + (1 - p) * 60, ch, f, WHITE, p * (1 - burst * .8))
        x += w


@scene("theorie")
def s_theorie(r, t, d, m):
    kb(r, t, d, 1.0, 1.06)
    title_lines(r, t, .1, ["LA THÉORIE", "DES JEUX"], 1180, 420, ("black", 130), WHITE, gap=1.05)
    # deux pions
    for i, (x, col) in enumerate(((330, BLUE), (620, RED))):
        p = eback(prog(t, .2 + i * .15, .7 + i * .15))
        y = 560 + (1 - p) * 200
        r.circle(x, y - 160, 50, col, p)
        r.poly([(x - 40, y - 110), (x + 40, y - 110), (x + 75, y + 60), (x - 75, y + 60)], col, p)
        r.rect(x - 95, y + 60, x + 95, y + 90, col, p, r=10)


@scene("interdep")
def s_interdep(r, t, d, m):
    kb(r, t, d, 1.0, 1.04)
    for i, (x, col, nm) in enumerate(((480, BLUE, "MOI"), (1440, RED, "LES AUTRES"))):
        p = eback(prog(t, i * .2, .5 + i * .2))
        r.circle(x, 430, 120 * p, col)
        r.text(x, 430, nm, ("black", 42 * max(p, .01)), WHITE)
    a = eout(prog(t, .6, 1.2))
    rot = t * 1.6
    r.arrow(640, 360, 1280, 360, AMBER, 8, a, p=a)
    r.arrow(1280, 500, 640, 500, AMBER, 8, a, p=eout(prog(t, .9, 1.5)))
    r.text(960, 320, "je choisis…", ("semi", 36), AMBER, a)
    r.text(960, 545, "…selon ce qu'ils vont choisir", ("semi", 36), AMBER, eout(prog(t, .9, 1.5)))
    q = eout(prog(t, frac(m, 0, .55), frac(m, 0, .7)))
    r.rect(360, 700, 1560, 820, WHITE, .07 * q, r=20)
    r.text(960, 760, "MA MEILLEURE DÉCISION DÉPEND DES AUTRES", ("black", 52), WHITE, q)


# ======================================================== arbre de jeu
NODES = {
    "T": (230, 560, "TIMES", BLUE),
    "N1": (650, 420, "NIXON", RED),
    "P": (1070, 300, "POST", TEAL),
    "N2": (1490, 200, "NIXON", RED),
}
EDGES = [  # (de, vers, étiquette, niveau d'apparition, principal)
    ("T", "N1", "publier", 1, True), ("T", (650, 720), "ne pas publier", 1, False),
    ("N1", "P", "poursuivre", 2, True), ("N1", (1070, 540), "laisser", 2, False),
    ("P", "N2", "publier", 3, True), ("P", (1490, 420), "se taire", 3, False),
    ("N2", (1820, 120), "poursuivre", 4, True), ("N2", (1820, 300), "laisser", 4, False),
]
ORDER = ["T", "N1", "P", "N2"]


def pos(k):
    return k if isinstance(k, tuple) else NODES[k][:2]


def tree(r, t, reveal, back=0.0, pubhl=0.0, think=0.0, title=None, ta=0):
    if title:
        title_lines(r, t, ta, [title], 960, 900 - 40, ("black", 64), AMBER)
    # arêtes
    for a, b, lab, lv, main in EDGES:
        q = eout(clamp(reveal - lv + 1))
        if q <= 0: continue
        (x0, y0), (x1, y1) = pos(a), pos(b)
        col = GREY if not main else WHITE
        if pubhl > 0 and lab == "publier":
            col = mixc(col, TEAL, pubhl)
        w = 6 + (8 * pubhl if (lab == "publier") else 0)
        r.line([(x0, y0), (lerp(x0, x1, q), lerp(y0, y1, q))], col, w, .9)
        if q > .6:
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            r.text(mx, my - 26, lab, ("semi", 28), col, eout((q - .6) / .4))
        if isinstance(b, tuple) and q >= 1:
            r.circle(x1, y1, 12, col, 1)
    # nœuds
    for i, k in enumerate(ORDER):
        q = eback(clamp(reveal - i))
        if q <= 0: continue
        x, y, nm, col = NODES[k]
        r.circle(x, y, 70 * q, col)
        r.text(x, y, nm, ("black", 26 * max(q, .01)), WHITE)
        r.circle(x - 56 * q, y - 56 * q, 22 * q, WHITE)
        r.text(x - 56 * q, y - 56 * q, str(i + 1), ("black", 26 * max(q, .01)), INK)
    # raisonnement à rebours
    if back > 0:
        path = [(1820, 210)] + [NODES[k][:2] for k in reversed(ORDER)]
        seg = back * (len(path) - 1)
        i = min(int(seg), len(path) - 2)
        f = seg - i
        px = lerp(path[i][0], path[i + 1][0], f); py = lerp(path[i][1], path[i + 1][1], f)
        for j in range(i + 1):
            r.line([path[j], path[j + 1] if j < i else (px, py)], AMBER, 14, .85)
        r.circle(px, py, 26, AMBER)
        r.circle(px, py, 40 + 10 * math.sin(t * 10), AMBER, .25)
        r.arrow(1500, 680, 1500 - 900 * eout(back), 680, AMBER, 10, 1)
        r.text(1500, 640, "À REBOURS", ("black", 44), AMBER, anchor="rm")
    if think > 0:
        for k, txt in (("T", "et si Nixon… ?"), ("N1", "et si le Post… ?"), ("P", "et si Nixon… ?")):
            x, y, _, _ = NODES[k]
            bx, by = x + 60, y + 150
            r.rect(bx - 10, by - 36, bx + r.tw(txt, ("bold", 30)) + 30, by + 36, WHITE, .95 * think, r=30)
            r.circle(x + 30, y + 95, 10, WHITE, think)
            r.text(bx + 10, by, txt, ("bold", 30), INK, think, anchor="lm")


@scene("tree")
def s_tree(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    reveal = 0.0
    for i in range(1, 5):
        if i < len(m):
            reveal = max(reveal, (i - 1) + eout(prog(t, M(m, i), M(m, i) + .8)))
    p = eout(prog(t, 0, .4))
    if t < M(m, 1):
        r.text(960, 880, "JEU SÉQUENTIEL : CHACUN SON TOUR", ("black", 56), AMBER, p)
    tree(r, t, reveal)


@scene("tree_back")
def s_tree_back(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    back = eout(prog(t, .3, M(m, 1) - .1))
    th = eout(prog(t, M(m, 1) + .4, M(m, 1) + 1.0))
    tree(r, t, 4, back, think=th)
    r.text(960, 880, "ON PART DE LA FIN ET ON REMONTE", ("black", 52), WHITE, eout(prog(t, .6, 1.0)) * (1 - th))
    r.text(960, 880, "CHAQUE JOUEUR ANTICIPE", ("black", 56), AMBER, th)


@scene("ingredients")
def s_ingredients(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    r.text(960, 140, "3 INGRÉDIENTS", ("black", 80), WHITE, eout(prog(t, 0, .4)))
    items = [("GAIN", "de publier", AMBER, .28), ("COÛT", "d'un procès", RED, .5), ("CHANCES", "de gagner", TEAL, .75)]
    for i, (nm, sub, col, f) in enumerate(items):
        ta = frac(m, 0, f) - .3
        p = eback(prog(t, ta, ta + .45))
        x = 420 + i * 540
        if p <= .02:
            continue
        r.rect(x - 220 * p, 260, x + 220 * p, 760, col, .14, outline=col, w=4, r=30)
        if p > .05:
            if i == 0:
                r.poly(star_pts(x, 430, 110 * p, 48 * p), col)
            elif i == 1:
                coins(r, x, 490, 5, 1, p)
            else:
                r.circle(x, 430, 105 * p, None, outline=col, w=18)
                r.d.pieslice([(x - 105 * p) * S, (330 + 105 - 105 * p) * S, (x + 105 * p) * S,
                              (430 + 105 * p) * S], -90, -90 + 360 * .7 * eout(prog(t, ta, ta + 1)),
                             fill=R.C(col, 1))
                r.circle(x, 430, 60 * p, INK)
                r.text(x, 430, "%", ("black", 60 * p), col)
        r.text(x, 620, nm, ("black", 70 * max(p, .01)), col)
        r.text(x, 690, sub, ("semi", 36 * max(p, .01)), WHITE)


# ======================================================== résolution
def bar(r, x, y, val, maxv, col, label, a=1.0, w=1100, h=90, vtxt=None):
    r.rect(x, y, x + w, y + h, DGREY, .5 * a, r=12)
    if val > .002:
        r.rect(x, y, x + max(h * .3, w * val / maxv), y + h, col, a, r=12)
    r.text(x, y - 40, label, ("black", 40), col, a, anchor="lm")
    if vtxt:
        r.text(x + max(0, w * val / maxv) + 24, y + h / 2, vtxt, ("black", 44), WHITE, a, anchor="lm")


@scene("gain")
def s_gain(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    g = eout(prog(t, .3, 1.3))
    lose = eout(prog(t, M(m, 1) + .5, M(m, 1) + 1.0))
    g *= (1 - lose * .999)
    bar(r, 360, 300, 20 * g, 22, AMBER, "GAIN DE PUBLIER", 1, vtxt="0" if lose > .9 else None)
    for i, (s, f) in enumerate((("prestige", .45), ("lecteurs", .62), ("fierté", .8))):
        p = eback(prog(t, frac(m, 0, f), frac(m, 0, f) + .3)) * (1 - lose)
        if p > .02:
            chip(r, 520 + i * 300, 470, s, AMBER, min(p, 1), 36 * p)
    if lose > 0:
        r.text(1600, 345, "PROCÈS PERDU", ("black", 44), RED, lose)
        cross(r, 1600, 450, 80, RED, lose)
    if len(m) > 2:
        c = eout(prog(t, M(m, 2), M(m, 2) + .8))
        bar(r, 360, 650, 2 * c, 22, RED, "COÛT DU PROCÈS", c)
        for i, s in enumerate(("argent", "temps", "énergie")):
            ta = frac(m, 2, .35 + i * .18)
            p = eback(prog(t, ta, ta + .3))
            if p > .02:
                chip(r, 760 + i * 280, 760, s, RED, min(p, 1), 34 * p, WHITE)


GX0, GX1, GY0, GY1, VMAX = 260, 1380, 800, 230, 22.0


def gx(p): return GX0 + (GX1 - GX0) * p
def gy(v): return GY0 - (GY0 - GY1) * v / VMAX


def graph(r, t, G, C, p=None, zones=1.0, thr=1.0, note=None, note_a=0.0, appear=1.0):
    a = appear
    r.line([(GX0, GY0), (GX1 + 30, GY0)], GREY, 4, a)
    r.line([(GX0, GY0), (GX0, GY1 - 40)], GREY, 4, a)
    for v, s in ((0, "0 %"), (.5, "50 %"), (1, "100 %")):
        r.text(gx(v), GY0 + 34, s, ("semi", 28), GREY, a)
    r.text((GX0 + GX1) / 2, GY0 + 82, "chances que le gouvernement GAGNE le procès →", ("semi", 30), GREY, a)
    ps = clamp(1 - C / G) if G > 0 else 0
    if zones > 0:
        r.rect(gx(0), GY1 - 30, gx(ps), GY0, TEAL, .13 * zones * a)
        r.rect(gx(ps), GY1 - 30, gx(1), GY0, RED, .18 * zones * a)
        if ps > .12:
            r.text((gx(0) + gx(ps)) / 2, GY1, "IL PUBLIE", ("black", 46), TEAL, zones * a)
        r.text(gx(1) + 20 if ps > .8 else (gx(ps) + gx(1)) / 2, GY1 - 70 if ps > .8 else GY1,
               "IL SE TAIT", ("black", 40 if ps > .8 else 46), RED, zones * a, anchor="mm")
    # courbes
    r.line([(gx(0), gy(G)), (gx(1), gy(0))], AMBER, 9, a)
    r.line([(gx(0), gy(C)), (gx(1), gy(C))], RED, 7, a)
    # légende
    r.text(1450, 300, "ESPOIR", ("black", 40), AMBER, a, anchor="lm")
    r.text(1450, 345, "= (1 − chances) × gain", ("semi", 28), AMBER, a, anchor="lm")
    r.text(1450, 430, "COÛT DU PROCÈS", ("black", 40), RED, a, anchor="lm")
    r.text(1450, 475, f"gain = {G:.0f}   coût = {C:.1f}", ("semi", 28), GREY, a, anchor="lm")
    if thr > 0:
        x = gx(ps)
        r.line([(x, GY0), (x, GY1 - 30)], WHITE, 4, thr * a)
        r.circle(x, gy(C), 14, WHITE, thr * a)
        r.text(1450, 560, f"SEUIL ≈ {ps * 100:.0f} %", ("black", 52), WHITE, thr * a, anchor="lm")
    if p is not None:
        x = gx(p); v = (1 - p) * G
        r.line([(x, GY0), (x, gy(v))], AMBER, 3, a * .7)
        r.circle(x, gy(v), 18, AMBER, a)
        r.circle(x, gy(v), 30 + 6 * math.sin(t * 8), AMBER, .3 * a)
        r.text(x, GY0 - 30, f"{p * 100:.0f} %", ("black", 30), WHITE, a)
    if note and note_a > 0:
        r.rect(1420, 640, 1880, 760, WHITE, .1 * note_a, r=18)
        r.text(1650, 700, note, ("black", 38), WHITE, note_a)


@scene("graph1")
def s_graph1(r, t, d, m):
    # répliques : 0 pas sûr, 1 publie, 2 à partir de quand, 3 presque certain, 4 aucune chance
    ap = eout(prog(t, 0, .6))
    p = .5
    if len(m) > 2:
        p = lerp(.5, .8, einout(prog(t, M(m, 2), M(m, 3))))
        p = lerp(p, .985, einout(prog(t, M(m, 3), frac(m, 3, .6))))
    zones = eout(prog(t, M(m, 1), M(m, 1) + .5)) * (1 - .0)
    thr = eout(prog(t, frac(m, 3, .5), frac(m, 3, .65)))
    note, na = None, 0
    if t < M(m, 1):
        note, na = "beaucoup à espérer", eout(prog(t, frac(m, 0, .5), frac(m, 0, .7)))
    elif len(m) > 4 and t >= M(m, 4):
        note, na = "≈ 0 chance de perdre", eout(prog(t, M(m, 4), M(m, 4) + .5))
    zooms = eout(prog(t, M(m, 4), M(m, 4) + 1.2)) if len(m) > 4 else 0
    r.cam["z"] = 1 + .45 * zooms + .02 * t / d
    r.cam["cx"] = lerp(960, 1390, zooms); r.cam["cy"] = lerp(540, 560, zooms)
    graph(r, t, 20, 1, p, zones=zones if zones > 0 else 0, thr=thr, note=note, note_a=na, appear=ap)
    if M(m, 1) <= t < M(m, 2):
        stamp(r, "SANS HÉSITER", 720, 520, t, M(m, 1) + .3, TEAL, 60, -6)


@scene("tree_back2")
def s_tree_back2(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    tree(r, t, 4, eout(prog(t, .2, d - .2)))


@scene("court")
def s_court(r, t, d, m):
    kb(r, t, d, 1.02, 1.08, 960, 460)
    p = eout(prog(t, 0, .7))
    court(r, 760, 470 + (1 - p) * 80, 1.0, p)
    title_lines(r, t, .3, ["COUR", "SUPRÊME"], 1180, 360, ("black", 110), WHITE, anchor="lm")
    r.text(1180, 560, "le plus haut tribunal du pays", ("semi", 40), GREY, eout(prog(t, .7, 1.1)), anchor="lm")
    if len(m) > 1:
        c = eout(prog(t, M(m, 1), M(m, 1) + .8))
        r.text(1180, 680, "COÛT DU PROCÈS", ("black", 40), RED, c, anchor="lm")
        r.rect(1180, 720, 1180 + 120 + 380 * c, 790, RED, c, r=10)
        r.text(1180 + 140 + 380 * c, 755, "↑↑", ("black", 50), RED, c, anchor="lm")


@scene("graph2")
def s_graph2(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    C = lerp(1, 2, eout(prog(t, .3, 1.4)))
    graph(r, t, 20, C, None, zones=1, thr=1, note="Cour suprême", note_a=eout(prog(t, 0, .5)))
    chip(r, 820, 140, "LE POST NE SE TAIT QUE S'IL EST PRESQUE SÛR DE PERDRE", WHITE, eout(prog(t, .8, 1.2)), 30)


@scene("nixon_think")
def s_nixon(r, t, d, m):
    kb(r, t, d, 1.0, 1.08, 760, 500)
    person(r, 760, 600, 2.0, (92, 54, 60))
    r.rect(560, 820, 960, 900, INK, .9, r=10)
    r.text(760, 860, "NIXON", ("black", 52), WHITE)
    for i in range(3):
        p = eback(prog(t, .2 + i * .15, .5 + i * .15))
        r.circle(930 + i * 70, 400 - i * 60, (16 + i * 10) * p, WHITE)
    p = eback(prog(t, .6, 1.0))
    r.circle(1380, 230, 170 * p, WHITE)
    r.text(1380, 230, "?", ("black", 200 * max(p, .01)), INK)


@scene("tree_pub")
def s_tree_pub(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    hl = eout(prog(t, .3, 1.0))
    tree(r, t, 4, pubhl=hl)
    r.text(960, 880, "LES DEUX JOURNAUX PUBLIENT, QUOI QU'IL ARRIVE", ("black", 50), TEAL, eout(prog(t, .7, 1.2)))


@scene("scale")
def s_scale(r, t, d, m):
    kb(r, t, d, 1.0, 1.04)
    tilt = lerp(0, .28, eback(prog(t, .5, 1.4)))
    balance(r, 960, 260, -tilt, "LAISSER PUBLIER", "RISQUER UN PROCÈS", RED, TEAL)
    r.text(960, 140, "POUR NIXON", ("black", 60), WHITE, eout(prog(t, 0, .4)))
    q = eback(prog(t, 1.4, 1.8))
    r.text(560, 230, "PIRE", ("black", 70 * max(q, .01)), RED)


@scene("gavel", "red")
def s_gavel(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    ang = lerp(-2.5, -3.25, eout(prog(t, 0, .2)))
    gavel(r, 1400, 760, ang, 1.4, AMBER)
    r.rect(900, 800, 1300, 840, (120, 80, 40), 1, r=8)
    if t > .2 and t < .5:
        k = 1 - (t - .2) / .3
        r.cam["sy"] += math.sin(t * 90) * 14 * k
    title_lines(r, t, .15, ["IL POURSUIT"], 760, 420, ("black", 150), WHITE)
    r.text(760, 560, "même sans être sûr de gagner", ("semi", 46), (255, 200, 200), eout(prog(t, .7, 1.2)))


@scene("reality")
def s_reality(r, t, d, m):
    st = M(m, 0)
    r.cam["z"] = 1.0 + .06 * prog(t, st, d)
    if t < st:
        return
    p = eback(prog(t, st, st + .4))
    r.text(960, 520, "ET LA RÉALITÉ ?", ("black", 170 * max(p, .01)), WHITE)


@scene("verdict")
def s_verdict(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    calendar(r, 330, 470, 30, "juin", 1971, t, 0, .8)
    p = eout(prog(t, frac(m, 0, .2), frac(m, 0, .35)))
    court(r, 1100, 380, .7, p, WHITE)
    q = eback(prog(t, frac(m, 0, .45), frac(m, 0, .55)))
    r.text(1100, 640, "6  –  3", ("black", 150 * max(q, .01)), AMBER)
    r.text(1100, 740, "à la majorité", ("semi", 38), GREY, q)
    stamp(r, "DROIT DE PUBLIER", 1100, 860, t, frac(m, 0, .72), TEAL, 70, -4)


# ======================================================== résultats
def rescard(r, t, d, n, l1, l2, col):
    kb(r, t, d, 1.0, 1.05)
    p = eout(prog(t, 0, .4))
    r.rect(0, 250, 1920 * p, 330, col, 1)
    r.text(200, 290, f"RÉSULTAT {n}", ("black", 52), INK, p, anchor="lm")
    for i in range(3):
        r.circle(1600 + i * 70, 290, 18, INK if i < n else (0, 0, 0), p if i < n else .25 * p)
    title_lines(r, t, .3, [l1, l2], 200, 480, ("black", 96), WHITE, gap=1.2, anchor="lm", cols=[WHITE, col])


@scene("res1")
def s_res1(r, t, d, m):
    rescard(r, t, d, 1, "Seules des chances extrêmes", "font taire la presse", AMBER)


@scene("graph3")
def s_graph3(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    graph(r, t, 20, 1, None, zones=1, thr=1, note="Times ou Post", note_a=eout(prog(t, .3, .8)))
    a = eout(prog(t, .6, 1.0))
    r.rect(gx(.95) - 6, GY1 - 36, gx(1) + 6, GY0 + 6, None, outline=RED, w=6, oa=a * (.6 + .4 * math.sin(t * 6)))


@scene("shield", "teal")
def s_shield(r, t, d, m):
    kb(r, t, d, 1.0, 1.05)
    p = eback(prog(t, 0, .5))
    cx, cy = 520, 480
    pts = [(cx - 180 * p, cy - 220 * p), (cx + 180 * p, cy - 220 * p), (cx + 180 * p, cy + 20 * p),
           (cx, cy + 240 * p), (cx - 180 * p, cy + 20 * p)]
    r.poly(pts, TEAL, 1)
    r.text(cx, cy - 30, "PRESSE", ("black", 54 * max(p, .01)), INK)
    title_lines(r, t, .3, ["UNE PRESSE LIBRE", "SE LAISSE TRÈS", "DIFFICILEMENT", "INTIMIDER"], 820, 320,
                ("black", 82), WHITE, gap=1.15, anchor="lm", cols=[TEAL, WHITE, WHITE, WHITE])


@scene("res2")
def s_res2(r, t, d, m):
    rescard(r, t, d, 2, "Le gain", "compte", AMBER)


@scene("small_story")
def s_small(r, t, d, m):
    kb(r, t, d, 1.0, 1.03)
    g = lerp(20, 2, eout(prog(t, .3, 1.4)))
    bar(r, 360, 420, g, 22, AMBER, "GAIN DE PUBLIER", 1, vtxt=f"{g:.0f}")
    chip(r, 960, 650, "UNE TOUTE PETITE HISTOIRE", WHITE, eout(prog(t, 1.0, 1.4)), 40)


@scene("graph4")
def s_graph4(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    G = lerp(20, 2, eout(prog(t, 0, 1.2)))
    graph(r, t, G, 1, None, zones=1, thr=1, note="risque modéré", note_a=eout(prog(t, 1.0, 1.4)))


@scene("big_story", "amber")
def s_big(r, t, d, m):
    r.cam["z"] = 1.0 + .1 * (1 - eout(prog(t, 0, .4)))
    g = lerp(2, 20, eback(prog(t, 0, .6)))
    bar(r, 300, 380, g, 22, AMBER, "LE SCOOP DES PENTAGON PAPERS", 1, w=1300, h=140)
    title_lines(r, t, .3, ["GIGANTESQUE"], 960, 720, ("black", 150), WHITE)


@scene("res3")
def s_res3(r, t, d, m):
    rescard(r, t, d, 3, "Les coûts jouent", "dans les deux sens", RED)
    a = eout(prog(t, .8, 1.3))
    r.arrow(1300, 720, 1750, 720, RED, 10, a, p=a)
    r.arrow(1750, 800, 1300, 800, RED, 10, a, p=a)


@scene("costs")
def s_costs(r, t, d, m):
    kb(r, t, d, 1.0, 1.02)
    second = len(m) > 1 and t >= M(m, 1)
    p2 = eout(prog(t, M(m, 1), M(m, 1) + 1.0)) if len(m) > 1 else 0
    tilt = lerp(.3, 0, p2) * eout(prog(t, .3, 1.2))
    balance(r, 960, 300, tilt, "GOUVERNEMENT", "JOURNAUX", RED, BLUE, sc=1.0)
    # poids "coût"
    r.text(960 + 340 * math.cos(tilt), 300 + 340 * math.sin(tilt) + 70, "COÛT", ("black", 36), WHITE,
           eout(prog(t, .3, .6)))
    r.text(960 - 340 * math.cos(tilt), 300 - 340 * math.sin(tilt) + 70, "COÛT", ("black", 36), WHITE, p2)
    res_a = eout(prog(t, frac(m, 0, .7), frac(m, 0, .85))) * (1 - p2)
    r.text(960, 870, "→ LES JOURNAUX SE TAISENT", ("black", 56), RED, res_a)
    if second:
        q = eout(prog(t, frac(m, 1, .45), frac(m, 1, .6)))
        r.text(960, 870, "→ NIXON NE POURSUIT PLUS, ILS PUBLIENT", ("black", 54), TEAL, q)


@scene("final_msg", "dark")
def s_final_msg(r, t, d, m):
    kb(r, t, d, 1.0, 1.06)
    p = eback(prog(t, 0, .4))
    r.text(960, 520, "LE MESSAGE FINAL", ("black", 140 * max(p, .01)), AMBER)


@scene("courage")
def s_courage(r, t, d, m):
    kb(r, t, d, 1.0, 1.04)
    for i in range(5):
        p = eout(prog(t, .1 + i * .08, .5 + i * .08))
        person(r, 420 + i * 270, 620 + (1 - p) * 60, 1.0, (70 + i * 8, 80 + i * 6, 96), p)
    title_lines(r, t, .3, ["PAS SEULEMENT", "LE COURAGE"], 960, 210, ("black", 96), WHITE, gap=1.1,
                cols=[WHITE, AMBER])
    r.text(960, 880, "de quelques journalistes", ("semi", 44), GREY, eout(prog(t, .9, 1.3)))


@scene("incitations", "amber")
def s_incit(r, t, d, m):
    kb(r, t, d, 1.0, 1.04)
    title_lines(r, t, 0, ["LES INCITATIONS"], 960, 250, ("black", 130), AMBER)
    for i, (s, f) in enumerate((("QUI PAIE QUOI ?", .45), ("QUI RISQUE QUOI ?", .72))):
        ta = frac(m, 0, f)
        p = eback(prog(t, ta, ta + .4))
        r.rect(960 - 520 * p, 430 + i * 190, 960 + 520 * p, 560 + i * 190, WHITE, .1, r=26)
        r.text(960, 495 + i * 190, s, ("black", 78 * max(p, .01)), WHITE)


@scene("last_q")
def s_last_q(r, t, d, m):
    kb(r, t, d, 1.0, 1.08)
    p = eback(prog(t, 0, .4))
    r.text(960, 520, "UNE DERNIÈRE QUESTION", ("black", 120 * max(p, .01)), WHITE)


@scene("final_q")
def s_final_q(r, t, d, m):
    kb(r, t, d, 1.0, 1.04)
    title_lines(r, t, 0, ["Si les procès avaient coûté", "beaucoup moins cher", "au gouvernement…"],
                960, 200, ("black", 76), WHITE, gap=1.18, cols=[WHITE, AMBER, WHITE])
    q = eout(prog(t, frac(m, 0, .55), frac(m, 0, .7)))
    r.text(960, 530, "…auriez-vous pris le risque de publier ?", ("xbold", 58), WHITE, q)
    for i, (s, col) in enumerate((("PUBLIER", TEAL), ("SE TAIRE", GREY))):
        p = eback(prog(t, frac(m, 0, .8) + i * .15, frac(m, 0, .8) + i * .15 + .4))
        pulse = 1 + .03 * math.sin(t * 5 + i * 3)
        x = 700 + i * 520
        w, h = 210 * p * pulse, 70 * p * pulse
        r.rect(x - w, 690 - h, x + w, 690 + h, col, 1, r=h)
        r.text(x, 690, s, ("black", 52 * max(p, .01)), INK)
    e = eout(prog(t, m[0][1] + .8, m[0][1] + 1.5))
    r.text(960, 850, "Répondez en commentaire", ("semi", 40), AMBER, e)
