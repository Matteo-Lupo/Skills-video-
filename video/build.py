# -*- coding: utf-8 -*-
"""Construit la vidéo complète : python3 build.py [--preview SECONDES...] [--out FICHIER]"""
import os, sys, json, math, bisect, subprocess, argparse
import numpy as np
from multiprocessing import Pool
from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gfx import *
import scenes as SC
from script_lines import LINES, CHAPTERS, CHAPTER_START
import audio as AU

FPS = 25
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.environ.get("WORK", os.path.join(HERE, "build"))


# ------------------------------------------------------------------ timeline
def build_timeline():
    clips = AU.tts(LINES, os.path.join(WORK, "tts"))
    t = 0.0
    tl = []
    for ln, c in zip(LINES, clips):
        t += ln["pre"]
        dur = len(c) / AU.SR
        tl.append(dict(start=t, dur=dur, **ln))
        t += dur + 0.32 + ln["pause"]
    total = t + 0.5
    # scènes
    scenes = []
    for i, ln in enumerate(tl):
        if ln["scene"]:
            st = ln["start"] - ln["pre"] if ln["pre"] else ln["start"]
            scenes.append(dict(name=ln["scene"], start=st if i else 0.0, lines=[i]))
        else:
            scenes[-1]["lines"].append(i)
    for k, s in enumerate(scenes):
        s["end"] = scenes[k + 1]["start"] if k + 1 < len(scenes) else total
        s["marks"] = [(tl[i]["start"] - s["start"], tl[i]["dur"]) for i in s["lines"]]
    return tl, scenes, total, clips


# ------------------------------------------------------------------ sous-titres
def sub_chunks(tl):
    out = []
    for ln in tl:
        words = ln["text"].split()
        chunks, cur = [], []
        for w in words:
            if cur and len(" ".join(cur + [w])) > 44:
                chunks.append(cur); cur = []
            cur.append(w)
        if cur:
            chunks.append(cur)
        tot = sum(len(" ".join(c)) for c in chunks)
        t = ln["start"]
        kwords = set()
        for k in ln["kw"]:
            for w in k.split():
                if len(norm(w)) > 3 or norm(w)[:1].isdigit() or len(k.split()) == 1:
                    kwords.add(norm(w))
        for c in chunks:
            d = ln["dur"] * len(" ".join(c)) / tot
            out.append(dict(start=t, end=t + d, words=c, kw=kwords))
            t += d
        out[-1]["end"] = ln["start"] + ln["dur"] + 0.18
    return out


def norm(w):
    return w.lower().strip(".,:;?!«»()'’").replace("’", "'")


def draw_subs(im, T, chunks, starts):
    i = bisect.bisect_right(starts, T) - 1
    if i < 0:
        return
    c = chunks[i]
    if T > c["end"]:
        return
    d = ImageDraw.Draw(im, "RGBA")
    f = font("bold", 22)  # font() multiplie par S=2 -> 44 px
    space = f.getlength(" ")
    widths = [f.getlength(w) for w in c["words"]]
    total = sum(widths) + space * (len(widths) - 1)
    x = (W - total) / 2
    y = 1000
    a = min(1, (T - c["start"]) / 0.08)
    d.rounded_rectangle([x - 28, y - 38, x + total + 28, y + 38], radius=14, fill=(0, 0, 0, int(165 * a)))
    for w, wd in zip(c["words"], widths):
        k = norm(w) in c["kw"] or any(norm(p) in c["kw"] for p in w.split("'")[1:])
        col = AMBER if k else WHITE
        d.text((x, y), w, font=f, fill=col + (int(255 * a),), anchor="lm")
        x += wd + space


def draw_hud(im, T, tl, total):
    d = ImageDraw.Draw(im, "RGBA")
    f = font("bold", 11)
    d.text((40, 38), "PENTAGON PAPERS · 1971", font=f, fill=(243, 239, 230, 150), anchor="lm")
    bounds = [tl[i]["start"] - tl[i]["pre"] for i in CHAPTER_START] + [total]
    x0, wseg, gap = 1920 - 40 - 4 * 110 - 3 * 8, 110, 8
    for k in range(4):
        a, b = bounds[k], bounds[k + 1]
        p = clamp((T - a) / (b - a))
        xx = x0 + k * (wseg + gap)
        d.rounded_rectangle([xx, 34, xx + wseg, 42], radius=4, fill=(255, 255, 255, 50))
        if p > 0:
            d.rounded_rectangle([xx, 34, xx + max(8, wseg * p), 42], radius=4, fill=AMBER + (230,))
    cur = max(k for k in range(4) if T >= bounds[k] or k == 0)
    d.text((1920 - 40, 66), CHAPTERS[cur].upper(), font=font("semi", 10), fill=(243, 239, 230, 140), anchor="rm")


# ------------------------------------------------------------------ post-traitement
_VIG = None
_GRAIN = None


def post(im, cam):
    global _VIG, _GRAIN
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W]
        dd = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2)
        _VIG = (1 - 0.38 * np.clip(dd - 0.35, 0, 1) ** 1.5)[..., None].astype(np.float32)
        rng = np.random.default_rng(7)
        _GRAIN = [rng.normal(0, 2.5, (H, W, 1)).astype(np.float32) for _ in range(6)]
    a = np.asarray(im).astype(np.float32)
    if cam.get("rgb", 0) > 0:
        s = int(cam["rgb"])
        a[..., 0] = np.roll(a[..., 0], s, axis=1)
        a[..., 2] = np.roll(a[..., 2], -s, axis=1)
    if cam.get("flash", 0) > 0:
        a = a + (255 - a) * cam["flash"]
    a = a * _VIG + _GRAIN[0]
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def camera(im, cam):
    if cam["ang"]:
        im = im.rotate(cam["ang"], resample=Image.BILINEAR, fillcolor=(10, 6, 8))
    z = max(1.0, cam["z"])
    w, h = W * S / z, H * S / z
    cx = clamp(cam["cx"] * S + cam["sx"] * S, w / 2, W * S - w / 2)
    cy = clamp(cam["cy"] * S + cam["sy"] * S, h / 2, H * S - h / 2)
    if z < 1.0001 and abs(cam["sx"]) < .01 and abs(cam["sy"]) < .01:
        return im.reduce(2)
    return im.resize((W, H), Image.BILINEAR, box=(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2),
                     reducing_gap=2.0)


# ------------------------------------------------------------------ rendu d'une image
G = {}


def init_worker(data):
    G.update(data)
    G["sstarts"] = [s["start"] for s in G["scenes"]]
    G["chunks"] = sub_chunks(G["tl"])
    G["cstarts"] = [c["start"] for c in G["chunks"]]


def render_frame(fi):
    T = fi / FPS
    scs = G["scenes"]
    k = max(0, bisect.bisect_right(G["sstarts"], T) - 1)
    s = scs[k]
    fn, bg = SC.SCENES[s["name"]]
    r = R(bg)
    t = T - s["start"]
    d = s["end"] - s["start"]
    fn(r, t, d, s["marks"])
    # transition d'entrée : léger flash/punch
    if k > 0 and t < 0.12:
        r.cam["flash"] = max(r.cam["flash"], 0.25 * (1 - t / 0.12))
    r.cam["_f"] = fi
    im = camera(r.im, r.cam)
    im = post(im, r.cam)
    draw_hud(im, T, G["tl"], G["total"])
    draw_subs(im, T, G["chunks"], G["cstarts"])
    return im


def render_range(args):
    a, b, path = args
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                          "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "medium",
                          "-crf", "20", "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for fi in range(a, b):
        p.stdin.write(render_frame(fi).tobytes())
    p.stdin.close(); p.wait()
    return path


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--preview", nargs="*", type=float)
    ap.add_argument("--out", default=os.path.join(HERE, "pentagon_papers.mp4"))
    ap.add_argument("--jobs", type=int, default=os.cpu_count())
    ap.add_argument("--range", nargs=2, type=float)
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    tl, scenes, total, clips = build_timeline()
    data = dict(tl=tl, scenes=scenes, total=total)
    print(f"Durée totale : {total:.1f} s, {len(scenes)} scènes, {len(tl)} répliques")

    if args.preview is not None:
        init_worker(data)
        os.makedirs(os.path.join(WORK, "preview"), exist_ok=True)
        pts = args.preview or [s["start"] + 1.5 for s in scenes]
        for T in pts:
            fi = int(T * FPS)
            render_frame(fi).save(os.path.join(WORK, "preview", f"f_{T:07.2f}.jpg"), quality=85)
        return

    # ---- audio
    rng = np.random.default_rng(1)
    cs = [tl[i]["start"] - tl[i]["pre"] for i in CHAPTER_START] + [total]
    moods = ["tense", "light", "build", "warm"]
    sections = [(cs[k] if k else 0.0, cs[k + 1], moods[k]) for k in range(4)]
    mus = AU.music(total, sections, rng)
    voice = [(ln["start"], c) for ln, c in zip(tl, clips)]
    sfx = []
    for k, s in enumerate(scenes):
        if k:
            sfx.append((s["start"] - 0.12, "swoosh", 0.35))
    for ln in tl:
        if ln["sfx"]:
            sfx.append((ln["start"] - (0.05 if ln["sfx"] != "swoosh" else 0.2), ln["sfx"], 1.0))
    silences = [(ln["start"] - ln["pre"], ln["start"]) for ln in tl if ln["pre"] >= 0.5]
    wav = os.path.join(WORK, "mix.wav")
    AU.mix(total, voice, mus, sfx, silences, rng, wav)
    write_srt(tl, os.path.join(HERE, "pentagon_papers.srt"))
    json.dump(dict(total=total, scenes=[dict(name=s["name"], start=round(s["start"], 2), end=round(s["end"], 2))
                                        for s in scenes]), open(os.path.join(WORK, "timeline.json"), "w"), indent=1)

    # ---- vidéo
    nf = int(total * FPS)
    a0, a1 = 0, nf
    if args.range:
        a0, a1 = int(args.range[0] * FPS), int(args.range[1] * FPS)
    n = args.jobs * 3
    bounds = [a0 + (a1 - a0) * i // n for i in range(n + 1)]
    parts = [(bounds[i], bounds[i + 1], os.path.join(WORK, f"part{i:03d}.mp4")) for i in range(n)]
    with Pool(args.jobs, initializer=init_worker, initargs=(data,)) as pool:
        for i, p in enumerate(pool.imap(render_range, parts)):
            print(f"  segment {i + 1}/{n}", flush=True)
    lst = os.path.join(WORK, "parts.txt")
    with open(lst, "w") as f:
        for _, _, p in parts:
            f.write(f"file '{p}'\n")
    ss = a0 / FPS
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-ss", f"{ss:.3f}", "-t", f"{(a1 - a0) / FPS:.3f}", "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart",
                    args.out], check=True)
    print("OK ->", args.out)


def write_srt(tl, path):
    def ts(x):
        h = int(x // 3600); m = int(x % 3600 // 60); s = x % 60
        return f"{h:02d}:{m:02d}:{int(s):02d},{int((s - int(s)) * 1000):03d}"
    with open(path, "w") as f:
        for i, c in enumerate(sub_chunks(tl), 1):
            f.write(f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{' '.join(c['words'])}\n\n")


if __name__ == "__main__":
    main()
