# -*- coding: utf-8 -*-
"""Voix (espeak-ng + MBROLA), musique générée et bruitages, puis mixage."""
import os, re, subprocess, wave
import numpy as np

SR = 44100

TTS_FIX = [
    (r"New York Times", "Niou York Taïmz"),
    (r"\bTimes\b", "Taïmz"),
    (r"Washington Post", "Washingtone Poste"),
    (r"\bPost\b", "Poste"),
    (r"Ellsberg", "Elsbergue"),
    (r"\bscoop\b", "scoupe"),
]


def read_wav(path):
    with wave.open(path) as w:
        sr, n, ch = w.getframerate(), w.getnframes(), w.getnchannels()
        a = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    if sr != SR:
        x = np.arange(int(len(a) * SR / sr)) * (sr / SR)
        a = np.interp(x, np.arange(len(a)), a).astype(np.float32)
    # retire les silences de début/fin
    nz = np.where(np.abs(a) > 0.01)[0]
    if len(nz):
        a = a[max(0, nz[0] - 200): nz[-1] + 800]
    return a


def write_wav(path, a):
    a = np.clip(a, -1, 1)
    st = np.stack([a, a], 1) if a.ndim == 1 else a
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())


def tts(lines, outdir, speed=118):
    os.makedirs(outdir, exist_ok=True)
    clips = []
    for i, ln in enumerate(lines):
        txt = ln["tts"] or ln["text"]
        voice = ln["voice"] or "mb-fr1"
        if voice.startswith("mb-"):
            for a, b in TTS_FIX:
                txt = re.sub(a, b, txt)
        p = os.path.join(outdir, f"l{i:02d}.wav")
        if not os.path.exists(p):
            subprocess.run(["espeak-ng", "-v", voice, "-s", str(speed), "-a", "80", "-w", p, txt],
                           check=True, stderr=subprocess.DEVNULL)
        a = read_wav(p)
        a = a / (np.abs(a).max() + 1e-6) * 0.85
        clips.append(a)
    return clips


# ------------------------------------------------------------------ musique
def nf(midi):
    return 440.0 * 2 ** ((midi - 69) / 12)


def pad_note(freq, n, rng):
    t = np.arange(n) / SR
    out = np.zeros(n, np.float32)
    for det in (-0.12, 0.0, 0.13):
        f = freq * 2 ** (det / 12)
        ph = rng.uniform(0, 6.28)
        for h, amp in ((1, 0.6), (2, 0.22), (3, 0.08), (4, 0.04)):
            out += amp * np.sin(2 * np.pi * f * h * t + ph * h)
    env = np.minimum(1, t / 1.2) * np.minimum(1, (n / SR - t) / 1.4)
    trem = 0.85 + 0.15 * np.sin(2 * np.pi * 0.25 * t + rng.uniform(0, 6))
    return out * env * trem / 3


def kick(n=int(0.35 * SR)):
    t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)).astype(np.float32)


def hat(rng, n=int(0.05 * SR)):
    t = np.arange(n) / SR
    no = rng.standard_normal(n).astype(np.float32)
    no = np.diff(no, prepend=0)  # passe-haut grossier
    return no * np.exp(-t * 90) * 0.25


def music(total, sections, rng):
    """sections: liste (t0, t1, mood) — mood: tense | light | build | warm."""
    N = int(total * SR) + SR
    out = np.zeros(N, np.float32)
    progs = {
        "tense": [(57, 60, 64), (53, 57, 60), (52, 55, 59), (53, 57, 60)],   # Am F Em F
        "light": [(57, 60, 64), (55, 59, 62), (53, 57, 60), (55, 59, 62)],   # Am G F G
        "build": [(50, 53, 57), (53, 57, 60), (57, 60, 64), (52, 56, 59)],   # Dm F Am E
        "warm":  [(48, 52, 55), (55, 59, 62), (57, 60, 64), (53, 57, 60)],   # C G Am F
    }
    bar = 4.0
    K = kick()
    for t0, t1, mood in sections:
        prog = progs[mood]
        t, k = t0, 0
        while t < t1:
            n = int(min(bar + 1.5, t1 - t + 1.5) * SR)
            i0 = int(t * SR)
            chord = prog[k % 4]
            seg = np.zeros(n, np.float32)
            for m in chord:
                seg += pad_note(nf(m), n, rng)
            seg += 0.7 * pad_note(nf(chord[0] - 24), n, rng)
            out[i0:i0 + n] += seg[: len(out) - i0] * 0.55
            t += bar; k += 1
        # pulsation
        beat = {"tense": 0.75, "light": 0.5, "build": 0.5, "warm": 0.75}[mood]
        t = t0
        j = 0
        while t < t1 - 0.3:
            i0 = int(t * SR)
            if mood in ("tense", "build") and j % 2 == 0:
                out[i0:i0 + len(K)] += K[: len(out) - i0] * (0.5 if mood == "tense" else 0.6)
            if mood in ("light", "build", "warm"):
                h = hat(rng)
                out[i0:i0 + len(h)] += h[: len(out) - i0] * (0.6 if j % 2 else 0.3)
            t += beat; j += 1
    return out


# ------------------------------------------------------------------ bruitages
def sfx_swoosh(rng):
    n = int(0.55 * SR)
    t = np.arange(n) / SR
    no = rng.standard_normal(n).astype(np.float32)
    spec = np.fft.rfft(no)
    fr = np.fft.rfftfreq(n, 1 / SR)
    spec *= np.exp(-((np.log(fr + 1) - np.log(1800)) ** 2) / 1.2)
    no = np.fft.irfft(spec, n)
    env = np.sin(np.pi * np.clip(t / 0.55, 0, 1)) ** 3
    o = no * env
    return o / np.abs(o).max() * 0.5


def sfx_impact(rng):
    n = int(1.2 * SR)
    t = np.arange(n) / SR
    f = 45 + 60 * np.exp(-t * 18)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3.5)
    no = rng.standard_normal(n) * np.exp(-t * 25) * 0.35
    o = (body + no).astype(np.float32)
    return o / np.abs(o).max() * 0.9


def sfx_glitch(rng):
    n = int(0.4 * SR)
    o = np.zeros(n, np.float32)
    for k in range(7):
        a = rng.integers(0, n - 2000); L = rng.integers(400, 3000)
        sq = np.sign(np.sin(2 * np.pi * rng.uniform(200, 1500) * np.arange(L) / SR))
        o[a:a + L] += sq[: n - a] * 0.25
    return o


def sfx_tick(rng):
    n = int(0.03 * SR)
    t = np.arange(n) / SR
    return (rng.standard_normal(n) * np.exp(-t * 300) * 0.4).astype(np.float32)


def mix(total, voice_events, music_track, sfx_events, silences, rng, out_path):
    N = int(total * SR) + SR
    v = np.zeros(N, np.float32)
    for t0, clip in voice_events:
        i = int(t0 * SR); v[i:i + len(clip)] += clip[: N - i]
    # enveloppe de voix pour le ducking
    env = np.abs(v)
    k = int(0.25 * SR)
    env = np.convolve(env, np.ones(k) / k, mode="same")
    env = np.clip(env / 0.12, 0, 1)
    m = music_track[:N]
    if len(m) < N:
        m = np.pad(m, (0, N - len(m)))
    gain = np.ones(N, np.float32)
    for a, b in silences:   # silence court avant une révélation
        ia, ib = int(a * SR), int(b * SR)
        ramp = int(0.15 * SR)
        gain[ia:ib] = 0
        gain[max(0, ia - ramp):ia] = np.linspace(1, 0, min(ramp, ia))
        gain[ib:ib + ramp] = np.linspace(0, 1, ramp)[: N - ib]
    fade = np.ones(N, np.float32)
    fo = int(3 * SR); fade[-fo:] = np.linspace(1, 0, fo)
    fi = int(1.0 * SR); fade[:fi] = np.linspace(0, 1, fi)
    mus = m / (np.abs(m).max() + 1e-6) * 0.17 * (1 - 0.55 * env) * gain * fade
    s = np.zeros(N, np.float32)
    bank = {"swoosh": sfx_swoosh, "impact": sfx_impact, "glitch": sfx_glitch, "tick": sfx_tick}
    for t0, kind, vol in sfx_events:
        c = bank[kind](rng) * vol
        i = int(t0 * SR)
        if i < 0 or i >= N:
            continue
        s[i:i + len(c)] += c[: N - i]
    outa = v * 1.0 + mus + s * 0.35
    outa = outa / max(1.0, np.abs(outa).max() / 0.95)
    write_wav(out_path, outa[: int(total * SR)])
