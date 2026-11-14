"""Soundtrack + narration for the Sun-vanished simulation. Writes work/sun.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
from soundlib import place, N
DUR = 49.6; n = int(DUR * SR); rng = np.random.default_rng(11)
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
def birds(d, lvl=0.035, seed=5):
    r = np.random.default_rng(seed); out = np.zeros(int(d * SR)); t0 = 0.2
    while t0 < d - 0.4:
        k = r.integers(2, 6); f0 = r.uniform(2600, 4800)
        for j in range(k):
            dd = r.uniform(0.05, 0.11); m = int(dd * SR); tt = np.arange(m) / SR; f = f0 * (1 + r.uniform(-0.15, 0.25) * tt / dd)
            ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dd) ** 2 * r.uniform(0.4, 1); a = int((t0 + j * r.uniform(0.09, 0.16)) * SR)
            if a + m < len(out): out[a:a + m] += ch
        t0 += r.uniform(0.35, 1.3)
    return out * lvl
def breeze(d, lvl=0.03):
    t = np.arange(int(d * SR)) / SR; return bp(noise(d), 200, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 6.1) ** 2) * lvl * env(d, 0.6, 0.6)
def wind(d, lvl=0.07):
    t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 180, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 3.7 + 1) ** 2) + bp(noise(d), 900, 2400) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 2.3)); return x * lvl * env(d, 0.8, 0.8)
LINES = [(0.4, "What if the Sun vanished, right now?"), (3.0, "You're in the park. It's midday. And the Sun has just vanished."), (6.6, "But look up. It's still there."),
 (8.6, "The last sunlight is still on its way. It needs about eight minutes and twenty seconds."),
 (13.8, "Even gravity isn't instant. It travels at the speed of light. So Earth keeps circling a Sun that is no longer there."),
 (21.2, "Then, time's up. The sky goes black. Stars come out at noon."),
 (25.3, "Earth lets go of its orbit. It flies off in a straight line, at about thirty kilometres a second."),
 (31.3, "Jupiter keeps shining for over an hour, on old sunlight."),
 (34.9, "Within a week, the average temperature is below freezing. Within a year, around minus seventy three degrees Celsius."),
 (42.5, "You never see the Sun as it is. Only as it was, eight minutes ago."), (47.2, "Follow for more.")]
bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
# beds: sunny park, then the diagram, then the dark, the cold, and the park again
place(bed, birds(8.6), 0.0, pan=-0.2); place(bed, birds(8.4, 0.02, 9), 0.2, pan=0.4); place(bed, breeze(8.8), 0.0); place(bed, pad(["A2", "E3", "A3", "C4"], 8.8, 1.5, 0.8, 0.03), 0.0)
place(bed, pad(["D2", "A2", "F3"], 12.6, 1.0, 1.0, 0.04), 8.4); place(bed, shimmer(12.2, 0.014), 8.5); place(bed, rumble(12.4, 0.03) * env(12.4, 2, 1), 8.4)
place(bed, birds(1.5, 0.03, 3), 20.8); place(bed, breeze(1.6), 20.7)
place(bed, pad(["C2", "G2", "C3", "D3"], 3.4, 0.05, 0.8, 0.045), 22.2); place(bed, rumble(3.2, 0.05) * env(3.2, 0.1, 1), 22.2)
place(bed, pad(["E2", "B2", "E3", "G3"], 9.8, 0.8, 0.6, 0.036), 25.1); place(bed, shimmer(9.6, 0.012), 25.2)
place(bed, wind(7.8, 0.06), 34.7); place(bed, pad(["B1", "F2", "B2", "D3"], 7.8, 0.8, 0.6, 0.04), 34.7)
place(bed, birds(6.6, 0.03, 12), 42.4, pan=0.2); place(bed, breeze(7.0), 42.4); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 7.2, 0.5, 1.6, 0.034), 42.4)
# effects
place(fx, riser(1.2, 0.05), 4.5); place(fx, boom(54, 1.2, 0.3), 5.6); place(fx, tick(900, 0.08), 5.6)
for ts in [8.5, 20.8, 25.2, 31.2, 34.8, 38.3]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
for k in range(0, 9): place(fx, tick(1000, 0.05), 8.9 + k * 1.33)                 # countdown ticks
place(fx, riser(1.6, 0.08), 20.5); place(fx, boom(38, 2.8, 0.6), 22.2)
place(fx, boom(52, 1.2, 0.25), 25.2); place(fx, whoosh(1.4, 0.07), 25.4); place(fx, boom(60, 0.9, 0.2), 34.8); place(fx, boom(48, 1.2, 0.25), 38.3)
place(fx, riser(1.4, 0.07), 41.0); place(fx, whoosh(0.9, 0.09), 42.3)
rep = []
for k, (ts, txt) in enumerate(LINES):
    v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
    rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
with wave.open(BASE + "/work/sun.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
