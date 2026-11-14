"""Soundtrack + narration for the Earth-stops-spinning simulation. Writes work/spin.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
from soundlib import place, N
DUR = 52.4; n = int(DUR * SR); rng = np.random.default_rng(15)
def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
def noise(d): return rng.normal(0, 1, int(d * SR))
def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
    return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
def surf(d, lvl=0.05):
    t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 250, 2600); sw = 0.55 + 0.45 * np.sin(2 * np.pi * t / 5.3 - 1) ** 2; return x * sw * lvl * env(d, 0.6, 0.6)
def boom(f=46, d=1.8, lvl=0.5):
    t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
def whoosh(d=0.7, lvl=0.09, up=True):
    m = int(d * SR); t = np.arange(m) / SR; x = noise(d); f = np.linspace(400, 5000, m) if up else np.linspace(5000, 400, m); ph = np.cumsum(f) / SR
    return (bp(x, 500, 6000) * 0.6 + np.sin(2 * np.pi * ph) * 0.05) * np.sin(np.pi * t / d) ** 2 * lvl
def riser(d=2.0, lvl=0.07):
    m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
def rumble(d, lvl=0.3):
    t = np.arange(int(d * SR)) / SR; x = lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5; return x * lvl
def crack(lvl=0.2):
    d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
def shimmer(d, lvl=0.022):
    t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(["C5", "E5", "G5", "B5", "D6"])) * env(d, 0.8, 1.0) * lvl
def tape(d=1.5, lvl=0.07):
    m = int(d * SR); t = np.arange(m) / SR; f = 2200 * np.exp(-t * 1.2) + 300 + 250 * np.sin(2 * np.pi * 9 * t); return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * 0.25 + bp(noise(d), 800, 5000)) * env(d, 0.05, 0.2) * lvl * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 14 * t)))
LINES = [(0.4, "What if the Earth stopped spinning, for one second?"), (3.2, "You're in a city on the equator."),
 (5.0, "The ground under you is moving east at sixteen hundred and seventy kilometres an hour. Faster than sound."),
 (12.4, "You feel nothing: everything moves with you."), (15.3, "In three seconds, the planet stops."),
 (18.7, "The ground stops. You don't. Nothing loose does."), (21.3, "You won't fly off into space. That takes forty thousand kilometres an hour."),
 (26.0, "And no wind hits you. The air is still travelling with you. It's the ground, and everything fixed to it, that comes at you."),
 (32.7, "In one second, you cross four hundred and sixty five metres."),
 (36.9, "Further from the equator, the ground moves slower. At sixty degrees north, half as fast. At the poles, you'd barely notice."),
 (44.6, "Then the Earth spins again. Too late."), (47.3, "You never feel speed. Only a change in speed."), (50.5, "Follow for more.")]
bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
def street(d, lvl=0.05):
    t = np.arange(int(d * SR)) / SR; return (lp(noise(d), 220, 2) * 2.2 + bp(noise(d), 300, 1800) * 0.35 * (0.6 + 0.4 * np.sin(2 * np.pi * t / 4.1) ** 2)) * lvl * env(d, 0.5, 0.5)
def rush(d, lvl=0.09):
    t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 180, 3200) * (0.75 + 0.25 * np.sin(2 * np.pi * 0.7 * t)) + lp(noise(d), 90, 4) * 3) * lvl * env(d, 0.4, 0.3)
# beds: street, space pads, the stopped second, aftermath, calm ending
place(bed, street(5.0), 0.0); place(bed, pad(["A2", "E3", "A3"], 5.2, 1.5, 0.8, 0.03), 0.0)
place(bed, pad(["D2", "A2", "F3"], 7.4, 0.8, 0.8, 0.036), 4.9); place(bed, shimmer(7.2, 0.012), 5.0)
place(bed, street(6.2), 12.1); place(bed, pad(["A2", "E3", "B3"], 3.2, 0.6, 0.4, 0.03), 12.2); place(bed, pad(["G2", "D3", "G3"], 3.2, 0.3, 0.2, 0.04), 15.2)
place(bed, pad(["D2", "A2", "D3", "F3"], 18.4, 0.3, 0.8, 0.04), 18.3); place(bed, rumble(2.9, 0.07) * env(2.9, 0.05, 0.5), 18.3)
place(bed, rush(10.8, 0.085), 25.7); place(bed, rumble(10.8, 0.04) * env(10.8, 1, 0.3), 25.7)
place(bed, pad(["E2", "B2", "E3", "G3"], 8.0, 0.5, 0.5, 0.036), 36.4)
place(bed, rumble(2.9, 0.12) * env(2.9, 0.05, 0.6), 44.3); place(bed, pad(["D2", "A2", "D3"], 2.9, 0.2, 0.5, 0.04), 44.3)
place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 5.6, 0.5, 1.6, 0.034), 46.9)
# effects
for k, ts in enumerate([15.3, 16.3, 17.3]): place(fx, tick(1000 + k * 120), ts)
place(fx, riser(1.8), 16.5); place(fx, boom(40, 2.4, 0.6), 18.3); place(fx, whoosh(1.1, 0.1), 18.35)
for ts in [5.0, 12.2, 21.1, 25.8, 36.5, 47.0]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
place(fx, boom(60, 0.9, 0.22), 21.1); place(fx, tick(820, 0.07), 23.0); place(fx, riser(2.2, 0.08), 34.3); place(fx, boom(48, 1.6, 0.4), 36.5)
for ts in [39.1, 41.5]: place(fx, tick(900, 0.08), ts)
place(fx, boom(42, 2.2, 0.55), 44.3)
for ts in [44.5, 45.0, 45.6, 46.2]: place(fx, crack(0.12 + rng.uniform(0, 0.08)), ts, pan=rng.uniform(-0.6, 0.6))
rep = []
for k, (ts, txt) in enumerate(LINES):
    v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
    rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
with wave.open(BASE + "/work/spin.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
