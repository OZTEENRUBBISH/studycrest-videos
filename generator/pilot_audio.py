"""Restrained soundtrack for the 'Spot the mistake' ads: pencil, a quiet clock, a soft flag, a warm resolve, optional clean voice.
Usage: pilot_audio.py <key> <speaker_id>"""
import os
BASE = os.path.dirname(os.path.abspath(__file__))
import sys, io, wave, subprocess, os, json
import numpy as np
from scipy import signal
import pilot as P
from soundlib import SR, place, N

rng = np.random.default_rng(3)
def bp(x, lo, hi): return signal.sosfilt(signal.butter(2, [lo, hi], "bandpass", fs=SR, output="sos"), x)

def pencil(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = bp(rng.normal(0, 1, n), 2200, 7000)
    strokes = np.zeros(n); pos = 0.0
    while pos < dur:
        L = rng.uniform(0.05, 0.16); i, j = int(pos * SR), int(min(dur, pos + L) * SR)
        strokes[i:j] = np.sin(np.linspace(0, np.pi, j - i)) ** 0.6 * rng.uniform(0.5, 1.0); pos += L + rng.uniform(0.02, 0.07)
    return x * strokes * 0.05

def clock(accent=False):
    t = np.arange(int(0.09 * SR)) / SR
    return (np.sin(2 * np.pi * (1250 if accent else 1050) * t) * np.exp(-t * 70) + rng.normal(0, 0.25, len(t)) * np.exp(-t * 500)) * (0.16 if accent else 0.11)

def blip(f=1760): t = np.arange(int(0.12 * SR)) / SR; return np.sin(2 * np.pi * f * t) * np.exp(-t * 45) * 0.07
def thump():
    t = np.arange(int(0.4 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(58 + 60 * np.exp(-t * 30)) / SR) * np.exp(-t * 9) * 0.30 + bp(rng.normal(0, 1, len(t)), 300, 900) * np.exp(-t * 40) * 0.05

def pad(notes, dur, attack, level):
    t = np.arange(int(dur * SR)) / SR; env = np.minimum(1, t / attack) * np.minimum(1, (dur - t) / 1.2).clip(0)
    return sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.25 * np.sin(2 * np.pi * N(nm) * 2 * t + k) for k, nm in enumerate(notes)) * env * level * (1 + 0.08 * np.sin(2 * np.pi * 0.3 * t))

_k = None
VOICES = {"blend": [("am_puck", 0.6), ("am_fenrir", 0.4)], "puck": [("am_puck", 1.0)], "fenrir": [("am_fenrir", 1.0)]}
def speak(text, vname):
    """Kokoro voice (Apache-2.0). 'blend' mixes two voices into one that exists nowhere else."""
    global _k
    from kokoro_onnx import Kokoro
    if _k is None: _k = Kokoro(BASE + "/kokoro/kokoro-v1.0.onnx", BASE + "/kokoro/voices-v1.0.bin")
    style = sum(_k.get_voice_style(n) * w for n, w in VOICES[vname])
    a, sr = _k.create(text.replace("StudyCrest", "Study Crest"), voice=style, speed=1.14, lang="en-us"); a = a.astype(np.float64)
    a = signal.resample_poly(a, SR, sr); idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 200): idx[-1] + 2400]
    a = signal.sosfilt(signal.butter(2, 90, "highpass", fs=SR, output="sos"), a)
    a = a + 0.35 * signal.sosfilt(signal.butter(1, 3500, "highpass", fs=SR, output="sos"), a)      # presence lift
    a = a / np.max(np.abs(a)); a = np.sign(a) * np.abs(a) ** 0.8                                    # gentle compression for punch
    return a / np.max(np.abs(a))

def swish():
    n = int(0.3 * SR); t = np.arange(n) / SR; return bp(rng.normal(0, 1, n), 900, 5000) * np.sin(np.pi * t / 0.3) ** 2 * 0.07

def build(key, sid):
    S = P.SPOTS[key]; tot = P.total(S); n = int(tot * SR); bed = np.zeros((n, 2)); fxb = np.zeros((n, 2)); vo = np.zeros(n); lines = []
    if S.get("feature"):
        t = 0.0
        for dur, parts, shot, cap, say in S["scenes"]:
            place(fxb, swish(), t); lines.append((t + 0.25, say))
            if shot is not None: place(fxb, blip(1568), t + 0.35)
            t += dur
        pay = end = t
        place(bed, pad(["A2", "E3", "A3"], end + 0.6, 1.2, 0.030), 0.0); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], tot - end, 0.5, 0.030), end)
    else:
        off = P.T_INTRO if S.get("intro") else 0.0; pay = off + P.T_PAY; end = off + P.T_END
        place(bed, pad(["A2", "E3", "A3"], pay + 0.6, 1.5, 0.030), 0.0); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], tot - pay, 0.5, 0.030), pay)
        if off:
            for st in (0.55, 0.95, 1.35): place(fxb, pencil(0.28), st, pan=0.2)
            place(fxb, swish(), off - 0.1); lines.append((0.15, S["intro_say"]))
        for tw in P.T_WRITE: place(fxb, pencil(1.0), off + tw, pan=-0.15)
        place(fxb, pencil(0.8), off + P.T_FIX + 0.2, pan=-0.15); place(fxb, pencil(0.8), off + P.T_FINAL, pan=-0.15)
        c0, c1 = P.T_COUNT; step = (c1 - c0) / 3
        for k in range(3): place(fxb, clock(), off + c0 + k * step)
        place(fxb, clock(True), off + c1)
        for i in range(S["wrong"]): place(fxb, blip(1568), off + P.T_CHECK[i] + 0.05)
        place(fxb, thump(), off + P.T_CHECK[S["wrong"]] + 0.02)
        place(fxb, blip(1760), off + P.T_FIX + 1.0); place(fxb, blip(2093), off + P.T_FINAL + 0.8)
        for bt in np.arange(0.0, off + P.T_CHECK[0], 0.6): place(fxb, thump() * 0.30, bt)
        for bt in np.arange(off + c1 - 0.9, off + c1, 0.18): place(fxb, clock() * 0.7, bt)
        lines += [(off + 0.12, "Try this one. Can you beat the AI?" if off else "Can you beat the AI? Spot the mistake!"),
                  (off + P.T_COUNT[0] + 0.05, "You've got three seconds!"), (off + P.T_CHECK[S["wrong"]] + 0.3, S["say_flag"]),
                  (pay + 0.15, "StudyCrest catches it while you're still writing!")]
    lines.append((end + 0.45, "Try it free for thirty days. You pay nothing!")); lines.append((end + 2.75, "Follow for a new one every day!")); lines.sort(); rep = []; tim = []
    for k, (ts, txt) in enumerate(lines):
        v = speak(txt, sid); v = v[: n - int(ts * SR)]; vo[int(ts * SR): int(ts * SR) + len(v)] += v * 0.6
        tim.append([round(ts, 3), round(len(v) / SR - 0.05, 3), txt])
        nxt = lines[k + 1][0] if k + 1 < len(lines) else tot; rep.append((round(ts, 2), round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.05 > nxt else "ok", txt[:38]))
    env = np.sqrt(signal.sosfilt(signal.butter(1, 6, "lowpass", fs=SR, output="sos"), vo ** 2).clip(0)); duck = 1 - 0.5 * np.clip(env / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.8 * SR):] = np.linspace(1, 0, int(0.8 * SR))
    m = np.tanh((bed * duck[:, None] + fxb + vo[:, None]) * fade[:, None]); m = m / np.max(np.abs(m)) * 0.8
    os.makedirs(BASE + "/timings", exist_ok=True); json.dump(tim, open(f"{BASE}/timings/{key}.json", "w"))
    path = f"{BASE}/wav/set-{key}.wav"
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    return path, rep

if __name__ == "__main__":
    # usage: pilot_audio.py wav <voice> [keys]   (voice + timings)   |   pilot_audio.py mux <outdir> [keys]
    mode, arg = sys.argv[1], sys.argv[2]; keys = sys.argv[3:] or list(P.SPOTS)
    for key in keys:
        idx = list(P.SPOTS).index(key) + 1
        if mode == "wav":
            path, rep = build(key, arg); print(key, [x for x in rep if x[2] != "ok"] or "all lines fit", flush=True)
        else:
            os.makedirs(arg, exist_ok=True); dst = f"{arg}/studycrest-{idx:02d}-{key}.mp4"
            r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{BASE}/silent/{key}.mp4", "-i", f"{BASE}/wav/set-{key}.wav", "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                                "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst + ".tmp.mp4"])
            if r.returncode == 0: os.replace(dst + ".tmp.mp4", dst)
            print(key, "mux rc", r.returncode, flush=True)
