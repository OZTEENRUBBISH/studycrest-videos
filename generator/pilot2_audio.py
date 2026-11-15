"""Soundtrack for the v2 'Spot the mistake' ads (pilot2.py): an upbeat beat from the first frame, a lively voice,
a countdown with a riser, a hit on the flag. Usage: pilot2_audio.py wav <voice> [keys] | pilot2_audio.py mux <outdir> [keys]"""
import os, sys, json, wave, subprocess
import numpy as np
from scipy import signal
import pilot as P
import pilot2 as P2
from soundlib import SR, place, N

BASE = os.path.dirname(os.path.abspath(__file__))
rng = np.random.default_rng(7)
BPM = 126.0; BEAT = 60.0 / BPM
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
def filt(x, kind, f, order=2): return signal.sosfilt(sos(kind, f, order), x)

# ---- voice -------------------------------------------------------------------------------------------------------
VOICES = {"hype": [("am_eric", 0.6), ("am_liam", 0.4)], "eric": [("am_eric", 1.0)], "liam": [("am_liam", 1.0)],
          "kore": [("af_kore", 1.0)], "sarah": [("af_sarah", 1.0)], "bright": [("af_sarah", 0.6), ("af_kore", 0.4)],
          "puck": [("am_puck", 1.0)]}
_k = None
def speak(text, vname, speed=1.2):
    """Kokoro voice (Apache-2.0). The blends are mixes of two voices, so they exist nowhere else."""
    global _k
    from kokoro_onnx import Kokoro
    if _k is None: _k = Kokoro(BASE + "/kokoro/kokoro-v1.0.onnx", BASE + "/kokoro/voices-v1.0.bin")
    style = sum(_k.get_voice_style(n) * w for n, w in VOICES[vname])
    a, sr = _k.create(text.replace("StudyCrest", "Study Crest"), voice=style, speed=speed, lang="en-us"); a = a.astype(np.float64)
    a = signal.resample_poly(a, SR, sr); idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 200): idx[-1] + 2400]
    a = filt(a, "highpass", 95)
    a = a + 0.45 * filt(a, "highpass", 3200, 1)                 # presence and air: brighter, more forward
    a = a / np.max(np.abs(a)); a = np.sign(a) * np.abs(a) ** 0.72  # firmer compression: every word lands
    return a / np.max(np.abs(a))

# ---- instruments -------------------------------------------------------------------------------------------------
def kick():
    t = np.arange(int(0.32 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(46 + 110 * np.exp(-t * 38)) / SR) * np.exp(-t * 11) * 0.9 + filt(rng.normal(0, 1, len(t)), "highpass", 2500) * np.exp(-t * 320) * 0.12
def hat(open_=False):
    t = np.arange(int((0.16 if open_ else 0.05) * SR)) / SR
    return filt(rng.normal(0, 1, len(t)), "highpass", 7000) * np.exp(-t * (26 if open_ else 95)) * 0.22
def clap():
    t = np.arange(int(0.22 * SR)) / SR; x = filt(rng.normal(0, 1, len(t)), "bandpass", [900, 3800])
    env = sum(np.exp(-np.clip(t - o, 0, None) * 150) * (t >= o) for o in (0.0, 0.011, 0.023)) * 0.5 + np.exp(-t * 28) * 0.5
    return x * env * 0.34
def bass(note, dur):
    t = np.arange(int(dur * SR)) / SR; f = N(note)
    x = np.sin(2 * np.pi * f * t) + 0.45 * np.sin(2 * np.pi * 2 * f * t) + 0.2 * np.sin(2 * np.pi * 3 * f * t)
    return x * np.minimum(1, t / 0.006) * np.exp(-t * 5.5) * 0.36
def pluck(note, dur=0.2, level=0.10):
    t = np.arange(int(dur * SR)) / SR; f = N(note)
    x = sum(np.sin(2 * np.pi * f * h * t) / h for h in (1, 2, 3, 4, 5))
    return x * np.exp(-t * 16) * np.minimum(1, t / 0.003) * level
def stab(notes, dur=0.42, level=0.085):
    t = np.arange(int(dur * SR)) / SR
    x = sum(np.sin(2 * np.pi * N(n) * t) + 0.4 * np.sin(2 * np.pi * N(n) * 2 * t) + 0.2 * np.sin(2 * np.pi * N(n) * 3.01 * t) for n in notes)
    return x * np.minimum(1, t / 0.004) * np.exp(-t * 7) * level
def riser(dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = rng.normal(0, 1, n); out = np.zeros(n); step = 2048
    for i in range(0, n, step):                                  # noise swept upward, block by block
        f = 500 + 6500 * (i / n) ** 2; seg = x[i:i + step]
        out[i:i + step] = signal.sosfilt(sos("bandpass", [f, f * 1.6]), seg)
    return out * (t / dur) ** 2 * 0.16
def tickk(f=1500):
    t = np.arange(int(0.07 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 90) + rng.normal(0, 0.2, len(t)) * np.exp(-t * 600)) * 0.16
def beep(f, dur=0.16, level=0.13):
    t = np.arange(int(dur * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.minimum(1, t / 0.004) * np.exp(-t * 14) * level
def impact():
    t = np.arange(int(0.7 * SR)) / SR
    return np.sin(2 * np.pi * np.cumsum(40 + 150 * np.exp(-t * 26)) / SR) * np.exp(-t * 6) * 0.7 + filt(rng.normal(0, 1, len(t)), "bandpass", [200, 2600]) * np.exp(-t * 22) * 0.22
def buzz():
    t = np.arange(int(0.34 * SR)) / SR; x = np.sign(np.sin(2 * np.pi * 148 * t)) + np.sign(np.sin(2 * np.pi * 157 * t))
    return filt(x, "lowpass", 1500) * np.minimum(1, t / 0.005) * np.minimum(1, (0.34 - t) / 0.05) * 0.075
def ding(notes=("E5", "A5", "C6")):
    t = np.arange(int(0.6 * SR)) / SR; out = np.zeros(len(t))
    for k, nm in enumerate(notes):
        o = int(k * 0.055 * SR); tt = t[: len(t) - o]; out[o:] += np.sin(2 * np.pi * N(nm) * tt) * np.exp(-tt * 7) * 0.085
    return out
def swish():
    n = int(0.3 * SR); t = np.arange(n) / SR; return filt(rng.normal(0, 1, n), "bandpass", [900, 5000]) * np.sin(np.pi * t / 0.3) ** 2 * 0.09
def pencil(dur):
    n = int(dur * SR); x = filt(rng.normal(0, 1, n), "bandpass", [2200, 7000]); strokes = np.zeros(n); pos = 0.0
    while pos < dur:
        L = rng.uniform(0.04, 0.10); i, j = int(pos * SR), int(min(dur, pos + L) * SR)
        strokes[i:j] = np.sin(np.linspace(0, np.pi, j - i)) ** 0.6 * rng.uniform(0.5, 1.0); pos += L + rng.uniform(0.015, 0.04)
    return x * strokes * 0.06

def groove(mus, t0, t1, bassline, full=True, arp=None, chords=None):
    """Four-on-the-floor between t0 and t1 (seconds), locked to the global beat grid."""
    b = int(np.ceil(t0 / BEAT - 1e-6))
    while b * BEAT < t1 - 0.05:
        t = b * BEAT
        place(mus, kick(), t)
        if full and b % 2 == 1: place(mus, clap(), t)
        place(mus, hat(), t, pan=0.25); place(mus, hat(open_=full), t + BEAT / 2, pan=-0.25)
        if full: place(mus, hat() * 0.6, t + BEAT / 4, pan=0.4); place(mus, hat() * 0.6, t + 3 * BEAT / 4, pan=-0.4)
        nt = bassline[(b // 4) % len(bassline)]
        place(mus, bass(nt, BEAT * 0.48), t + BEAT / 2); place(mus, bass(nt, BEAT * 0.3) * 0.8, t + 3 * BEAT / 4)
        if arp:
            seq = arp[(b // 4) % len(arp)]
            for s in range(4): place(mus, pluck(seq[(b * 4 + s) % len(seq)]), t + s * BEAT / 4, pan=0.5 * (-1) ** s)
        if chords and b % 4 in (0, 2): place(mus, stab(chords[(b // 4) % len(chords)]), t + (0 if b % 4 == 0 else BEAT * 0.75))
        b += 1

def build(key, vname):
    S = P.SPOTS[key]; T = P2.times(S); tot = T["total"]; n = int(tot * SR)
    mus = np.zeros((n, 2)); fxb = np.zeros((n, 2)); vo = np.zeros(n)
    AM = ["A1", "A1", "F1", "G1"]; ARP_A = [["A3", "C4", "E4", "A4"], ["A3", "C4", "E4", "A4"], ["F3", "A3", "C4", "F4"], ["G3", "B3", "D4", "G4"]]
    CM = ["C2", "G1", "A1", "F1"]; ARP_C = [["C4", "E4", "G4", "C5"], ["G3", "B3", "D4", "G4"], ["A3", "C4", "E4", "A4"], ["F3", "A3", "C4", "F4"]]
    CH_C = [["C4", "E4", "G4"], ["B3", "D4", "G4"], ["A3", "C4", "E4"], ["A3", "C4", "F4"]]
    c0, c1 = T["count"]; flag_t = T["check"][S["wrong"]]
    # 1. hook: beat from the very first frame, hit on the stamp
    groove(mus, 0.0, c0, AM, full=True, arp=ARP_A)
    for i in range(3): place(fxb, pencil(0.3), 0.05 + i * 0.12, pan=-0.2)
    place(fxb, impact(), T["stamp"]); place(fxb, buzz(), T["stamp"] + 0.02)
    # 2. countdown: the beat drops out, clock ticks speed up, a riser builds into the reveal
    place(fxb, swish(), c0 - 0.15); place(fxb, riser(c1 - c0), c0)
    step = (c1 - c0) / 3
    for k in range(3):
        place(fxb, beep(660 * 2 ** (k * 2 / 12.0)), c0 + k * step)
        for j in range(1, 2 + k * 2):                             # 1, 3, then 5 ticks inside each second
            place(fxb, tickk(1300 + 150 * k), c0 + k * step + j * step / (2 + k * 2))
        place(mus, kick() * 0.55, c0 + k * step); place(mus, kick() * 0.4, c0 + k * step + 0.16)   # heartbeat
    # 3. reveal
    for i in range(S["wrong"]): place(fxb, beep(1568, 0.1, 0.09), T["check"][i])
    place(fxb, impact(), flag_t); place(fxb, buzz(), flag_t + 0.03)
    groove(mus, flag_t + 0.35, T["pay"], AM, full=False, arp=ARP_A)
    place(fxb, pencil(0.7), T["fix"] + 0.1, pan=-0.15); place(fxb, ding(("E5", "A5")), T["fix"] + 0.85)
    place(fxb, pencil(0.7), T["final"], pan=-0.15); place(fxb, ding(), T["final"] + 0.75)
    # 4. payoff and end card: lift to the major key, full beat
    place(fxb, swish(), T["pay"] - 0.12); groove(mus, T["pay"], tot - 0.25, CM, full=True, arp=ARP_C, chords=CH_C)
    place(fxb, swish(), T["end"] - 0.12); place(fxb, ding(("G5", "C6", "E6")), T["end"] + 0.05)
    # voice
    lines = P2.script(S); rep = []; tim = []
    for k, (ts, txt, spd) in enumerate(lines):
        v = speak(txt, vname, spd); v = v[: n - int(ts * SR)]; vo[int(ts * SR): int(ts * SR) + len(v)] += v * 0.62
        tim.append([round(ts, 3), round(len(v) / SR - 0.05, 3), txt])
        nxt = lines[k + 1][0] if k + 1 < len(lines) else tot
        rep.append((round(ts, 2), round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.05 > nxt else "ok", txt[:40]))
    env = np.sqrt(filt(vo ** 2, "lowpass", 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(env / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.5 * SR):] = np.linspace(1, 0, int(0.5 * SR))
    m = np.tanh((mus * 0.60 * duck[:, None] + fxb + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    os.makedirs(BASE + "/timings", exist_ok=True); os.makedirs(BASE + "/wav", exist_ok=True)
    json.dump(tim, open(f"{BASE}/timings/v2-{key}.json", "w"))
    path = f"{BASE}/wav/v2-{key}.wav"
    with wave.open(path, "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    return path, rep

if __name__ == "__main__":
    mode, arg = sys.argv[1], sys.argv[2]; keys = [k for k in sys.argv[3:] if k != "-v"] or [k for k in P.SPOTS if not P.SPOTS[k].get("feature")]
    for key in keys:
        if mode == "wav":
            path, rep = build(key, arg); bad = [x for x in rep if x[2] != "ok"]; print(key, bad or "all lines fit", flush=True)
            if bad or "-v" in sys.argv:
                for r in rep: print("   ", r)
        else:
            os.makedirs(arg, exist_ok=True); dst = f"{arg}/v2-{key}.mp4"
            r = subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", f"{BASE}/silent/v2-{key}.mp4", "-i", f"{BASE}/wav/v2-{key}.wav", "-map", "0:v", "-map", "1:a",
                                "-c:v", "copy", "-af", "loudnorm=I=-14.5:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", dst])
            print(key, "mux rc", r.returncode, flush=True)
