"""Soundtrack + narration for the Chernobyl simulation. Writes work/chernobyl.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
from soundlib import place, N
DUR = 60.0; n = int(DUR * SR); rng = np.random.default_rng(11)
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
LINES = [(0.4, "Chernobyl. Second by second."), (2.5, "April twenty sixth, nineteen eighty six. One twenty three A M. You're in the control room of Reactor Four. A safety test is about to begin."),
 (11.2, "Inside the reactor: uranium fuel, cooled by water, wrapped in graphite. Tonight, almost every control rod has been pulled out."), (19.3, "The test starts. The pumps slow down. Water in the core flashes to steam. And in this design, more steam means more power."),
 (26.9, "Thirty six seconds in, the operators hit the emergency shutdown. A Z five."), (31.8, "The rods drop. But their tips are graphite. For a moment, they speed the reaction up."),
 (36.6, "Power surges to around a hundred times its design value. The fuel shatters. Steam blows the thousand tonne lid off the reactor."), (44.9, "The core is open to the sky. Unstable atoms pour out. Each one breaks apart, firing out radiation."),
 (51.7, "Iodine one thirty one halves every eight days. Caesium one thirty seven, every thirty years."), (57.9, "Follow for more.")]
bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
def hum(d, f=50, lvl=0.02): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2 * t) + 0.25 * np.sin(2 * np.pi * f * 3 * t)) * lvl * env(d, 0.5, 0.5)
def geiger(d, rate, lvl=0.1):
    x = np.zeros(int(d * SR)); t = 0.0
    while t < d: i = int(t * SR); c = tick(2600, lvl)[: len(x) - i]; x[i:i + len(c)] += c; t += rng.exponential(1.0 / rate(t))
    return x
def alarmtone(d, lvl=0.05): t = np.arange(int(d * SR)) / SR; return np.sign(np.sin(2 * np.pi * 620 * t)) * (np.sin(2 * np.pi * 2.2 * t) > 0) * lvl * env(d, 0.05, 0.3) * 0.5
place(bed, pad(["D2", "A2", "D3"], 11.4, 1.5, 1.0, 0.035), 0.0); place(bed, hum(5.2), 6.1); place(bed, lp(noise(6.2), 400) * 0.02 * env(6.2, 1, 1), 0.0)
place(bed, pad(["D2", "A2", "F3"], 8.3, 0.8, 0.8, 0.036), 11.2); place(bed, hum(8.3, 50, 0.012), 11.2)
place(bed, pad(["C2", "G2", "E3"], 7.7, 0.6, 0.5, 0.04), 19.3); st = bp(noise(7.6), 1800, 7000) * (np.arange(int(7.6 * SR)) / SR / 7.6) ** 1.5 * 0.05; place(bed, st * env(7.6, 0.1, 0.3), 19.2)
place(bed, alarmtone(4.9), 26.8); place(bed, hum(4.9, 50, 0.02), 26.8); place(bed, pad(["C2", "G2", "D3"], 5.0, 0.3, 0.4, 0.04), 26.8)
place(bed, pad(["B1", "F2", "B2", "D3"], 9.0, 0.5, 0.2, 0.05), 31.7); r2 = rumble(9.0, 0.1) * (np.arange(int(9.0 * SR)) / SR / 9.0) ** 2; place(bed, r2, 31.6)
place(bed, alarmtone(8.8, 0.035), 31.8)
fire = (bp(noise(7.2), 300, 3500) * 0.07 + rumble(7.2, 0.07)) * env(7.2, 0.05, 1.0); place(bed, fire, 40.6); place(bed, pad(["D2", "A2", "D3", "F3"], 7.2, 0.6, 1.0, 0.04), 40.8)
place(bed, pad(["A2", "E3", "A3", "C4"], 10.2, 0.8, 1.0, 0.03), 47.6); place(bed, geiger(12.0, lambda t: 6 + 26 * np.exp(-((t - 4.5) / 3.0) ** 2), 0.045), 45.0)
place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 2.6, 0.3, 1.2, 0.034), 57.4)
for ts in [6.2, 11.2, 26.8, 31.7, 44.8, 47.6, 51.6]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
place(fx, boom(60, 0.9, 0.2), 0.3); place(fx, tick(900, 0.14), 29.5); place(fx, boom(70, 0.5, 0.3), 29.55)
for k in range(8): place(fx, tick(1000, 0.05), 19.4 + k * 0.9)
place(fx, boom(55, 1.0, 0.25), 32.7); place(fx, riser(3.8, 0.12), 36.7); place(fx, boom(38, 3.2, 0.75), 40.6); place(fx, crack(0.5), 40.62); place(fx, boom(46, 2.4, 0.5), 41.35); place(fx, crack(0.35), 41.4)
for ts in [42.2, 42.9, 43.6, 44.1]: place(fx, crack(0.12), ts, pan=rng.uniform(-0.6, 0.6))
rep = []
for k, (ts, txt) in enumerate(LINES):
    v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
    rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
with wave.open(BASE + "/work/chernobyl.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
