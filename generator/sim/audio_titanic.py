"""Soundtrack + narration for the Titanic simulation. Writes work/titanic.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
from soundlib import place, N
DUR = 53.4; n = int(DUR * SR); rng = np.random.default_rng(1912)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
def noise(d): return rng.normal(0, 1, int(d * SR))
def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
    return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
def swell(d, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 180, 1600); sw = 0.5 + 0.5 * np.sin(2 * np.pi * t / 6.1 - 1) ** 2; return x * sw * lvl * env(d, 0.8, 0.8)
def engine(d, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; th = 0.6 + 0.4 * np.maximum(0, np.sin(2 * np.pi * 2.5 * t)) ** 3; return (np.sin(2 * np.pi * 38 * t) + 0.5 * np.sin(2 * np.pi * 76 * t) + lp(noise(d), 120) * 0.6) * th * lvl * env(d, 0.6, 0.8)
def boom(f=46, d=1.8, lvl=0.5):
    t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
def whoosh(d=0.7, lvl=0.09, up=True):
    m = int(d * SR); t = np.arange(m) / SR; x = noise(d); f = np.linspace(400, 5000, m) if up else np.linspace(5000, 400, m); ph = np.cumsum(f) / SR
    return (bp(x, 500, 6000) * 0.6 + np.sin(2 * np.pi * ph) * 0.05) * np.sin(np.pi * t / d) ** 2 * lvl
def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
def bell(lvl=0.1, f=880): t = np.arange(int(1.6 * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 3.2) * lvl
def rumble(d, lvl=0.3):
    t = np.arange(int(d * SR)) / SR; x = lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5; return x * lvl
def scrape(d=2.6, lvl=0.16):
    t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 300, 2400) * (0.6 + 0.4 * np.sin(2 * np.pi * 13 * t)) + lp(noise(d), 120, 4) * 4; return x * env(d, 0.15, 1.6) * lvl
def crack(lvl=0.2):
    d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
def groan(d=2.4, f0=70, f1=48, lvl=0.12):
    m = int(d * SR); t = np.arange(m) / SR; ph = np.cumsum(np.linspace(f0, f1, m)) / SR; return (np.sin(2 * np.pi * ph) + 0.4 * np.sin(2 * np.pi * ph * 2.02) + 0.2 * np.sign(np.sin(2 * np.pi * ph * 3))) * env(d, 0.5, 1.0) * lvl
def rush(d, lvl=0.05):
    t = np.arange(int(d * SR)) / SR; return bp(noise(d), 500, 5000) * (t / d) ** 0.8 * env(d, 0.3, 0.5) * lvl
LINES = [(0.4, "Titanic. Minute by minute."), (2.3, "April fourteenth, nineteen twelve. Eleven forty P M. You're on deck. No moon. A flat, freezing sea."),
 (9.0, "A lookout spots ice. Moments later, Titanic hits it."), (12.6, "You feel a shudder. Nothing more."),
 (14.8, "But the iceberg didn't tear one huge gash. It opened six thin tears. In total, barely more than one square metre."),
 (22.4, "Titanic can float with four compartments flooded. Water enters at least five."), (27.7, "Her designer checks the damage. She will sink."),
 (30.6, "The first lifeboat leaves less than half full. There are seats for barely half the people on board."),
 (36.3, "The bow goes under. The stern rises. At two eighteen, the lights go out, and the ship breaks in two."),
 (42.8, "Two twenty A M. She's gone. Around fifteen hundred people are lost."), (47.4, "Not one great wound. Small ones, in too many places."), (51.3, "Follow for more.")]
bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
place(bed, pad(["D2", "A2", "D3"], 15.0, 1.5, 1.0, 0.032), 0.0); place(bed, engine(11.6), 0.0); place(bed, swell(14.8), 0.0)
place(bed, pad(["C2", "G2", "E3"], 8.0, 0.8, 0.8, 0.034), 14.6); place(bed, rush(7.4, 0.03), 15.0)
place(bed, pad(["B1", "F2", "D3"], 8.4, 0.6, 0.6, 0.04), 22.3); place(bed, rush(8.0, 0.055), 22.4)
place(bed, pad(["A1", "E2", "C3", "E3"], 6.0, 0.6, 0.6, 0.04), 30.4); place(bed, swell(6.0, 0.03), 30.4)
place(bed, pad(["A1", "E2", "A2", "C3"], 6.8, 0.5, 0.4, 0.048), 36.2); place(bed, rumble(6.6, 0.05) * env(6.6, 2.5, 0.4), 36.2)
place(bed, swell(10.6, 0.028), 42.8); place(bed, pad(["F2", "C3", "A3"], 4.8, 1.2, 1.2, 0.022), 42.9)
place(bed, pad(["C3", "G3", "C4", "E4", "G4"], 6.0, 1.0, 1.6, 0.03), 47.3)
place(fx, boom(60, 0.9, 0.2), 0.3)
for ts in [9.0, 9.35, 9.7]: place(fx, bell(0.09), ts)                      # the lookout's bell
for ts in [2.3, 10.8, 14.8, 30.6, 36.3, 47.4]: place(fx, whoosh(0.55, 0.06), ts - 0.25)
place(fx, scrape(), 11.4); place(fx, boom(50, 1.4, 0.3), 11.5)
for k, ts in enumerate([22.9, 23.4, 23.9, 24.4]): place(fx, tick(900 + k * 60, 0.08), ts)
place(fx, boom(58, 1.0, 0.3), 25.3); place(fx, tick(1500, 0.1), 25.3)
place(fx, groan(), 37.0); place(fx, groan(2.2, 62, 40, 0.14), 39.0)
place(fx, tick(500, 0.12), 40.2); place(fx, boom(40, 2.6, 0.55), 41.1); place(fx, crack(0.4), 41.12); place(fx, crack(0.25), 41.5); place(fx, groan(2.6, 55, 30, 0.14), 41.6)
place(fx, rush(2.6, 0.08)[::-1].copy(), 43.2)
rep = []
for k, (ts, txt) in enumerate(LINES):
    v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
    rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
with wave.open(BASE + "/work/titanic.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
