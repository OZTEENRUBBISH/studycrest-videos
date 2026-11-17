"""Soundtrack + narration for the empty-space-in-atoms simulation. Writes work/atoms.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 46.0
LINES = [(0.4, "What if you removed all the empty space from your atoms?"),
 (3.5, "You'd shrink to a speck smaller than a grain of dust. And you'd weigh exactly the same."),
 (8.5, "Zoom into your hand. Past skin and cells, down to a single atom."),
 (12.7, "If its nucleus were a pea, the atom would be as wide as a stadium."),
 (16.8, "Nearly all of your mass sits in that pea. The rest is space."),
 (20.4, "Squeeze the space out of everyone, and the whole human race would fit inside a sugar cube."),
 (25.8, "But here's the catch. That space isn't really empty. Electrons fill it like a cloud, and they refuse to be squeezed."),
 (32.8, "They push other atoms away. So when you touch a table, what you feel is electrons pushing back."),
 (39.0, "You are mostly empty space. And that space is what makes you solid."), (43.4, "Follow for more.")]
CHUNKS = [[], ["You'd shrink to a speck", "smaller than<br>a <em>grain of dust</em>.", "And you'd weigh<br><em>exactly the same</em>."],
 ["Zoom into your hand.", "Past skin and cells,", "down to a <em>single atom</em>."],
 ["If its nucleus were a <em>pea</em>,", "the atom would be as wide<br>as a <em>stadium</em>."],
 ["Nearly all of your <em>mass</em><br>sits in that pea.", "The rest is <em>space</em>."],
 ["Squeeze the space<br>out of everyone,", "and the whole human race", "would fit inside<br>a <em>sugar cube</em>."],
 ["But here's the catch.", "That space isn't<br>really <em>empty</em>.", "Electrons fill it<br>like a <em>cloud</em>,", "and they refuse<br>to be <em>squeezed</em>."],
 ["They push other<br>atoms away.", "So when you touch a table,", "what you feel is electrons<br><em>pushing back</em>."],
 ["You are mostly<br><em>empty space</em>.", "And that space is what<br>makes you <em>solid</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(17)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def clicks(d, rate, lvl=0.06, seed=3, f0=2400, f1=5200):
        """Geiger-style clicks at `rate` per second (random, like real decays)."""
        out = np.zeros(int(d * SR)); r = np.random.default_rng(seed); t0 = 0.0
        while True:
            t0 += r.exponential(1 / rate)
            if t0 > d - 0.03: break
            tt = np.arange(int(0.012 * SR)) / SR; c = np.sin(2 * np.pi * r.uniform(f0, f1) * tt) * np.exp(-tt * 600) * r.uniform(0.5, 1); i = int(t0 * SR); out[i:i + len(c)] += c
        return out * lvl
    def zap(lvl=0.1):
        d = 0.28; m = int(d * SR); t = np.arange(m) / SR; return (np.sin(2 * np.pi * np.cumsum(np.linspace(3200, 500, m)) / SR) * 0.6 + hp(noise(d), 3000) * 0.4) * np.exp(-t * 16) * lvl
    def room(d, lvl=0.012): return (lp(noise(d), 160, 2) * 2 + np.sin(2 * np.pi * 50 * np.arange(int(d * SR)) / SR) * 0.35) * env(d, 0.5, 0.5) * lvl
    def city(d, lvl=0.03): return (lp(noise(d), 300, 2) * 2.2 + bp(noise(d), 300, 1500) * 0.25) * env(d, 0.6, 1.2) * lvl
    def klaxon(d, lvl=0.05):
        t = np.arange(int(d * SR)) / SR; return np.sign(np.sin(2 * np.pi * 520 * t)) * (np.sin(2 * np.pi * 1.45 * t) > 0) * lp(np.ones(len(t)), 800) * lvl * env(d, 0.05, 0.1)
    def beep(f=2525, d=0.25, lvl=0.035): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, 0.005, 0.02) * lvl
    def hiss(d, lvl=0.08, a=0.02, r=0.6): return hp(noise(d), 2500) * env(d, a, r, 1.5) * lvl
    def whir(d, lvl=0.04):
        t = np.arange(int(d * SR)) / SR; f = 60 + 160 * np.minimum(1, t / 1.2); return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)) * env(d, 0.3, 0.4) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def radio(d, lvl=0.012): return bp(noise(d), 600, 2600) * env(d, 0.05, 0.1) * lvl
    def splash(lvl=0.2):
        d = 1.6; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 300, 5000) * np.exp(-t * 3.2) + lp(noise(d), 200) * np.exp(-t * 5) * 1.5) * np.minimum(1, t / 0.02) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the room, the dive, the stadium, the globe and the cafe, the atom, the touch, the room again
    place(bed, room(8.4, 0.012), 0.0); place(bed, pad(["D2", "A2", "D3", "F3"], 8.5, 0.8, 0.8, 0.036), 0.0); place(bed, shimmer(3.2, 0.014), 0.2)
    place(bed, pad(["B1", "F2", "D3", "A3"], 4.5, 0.4, 0.5, 0.042), 8.2); place(bed, whir(4.2, 0.02), 8.3); place(bed, shimmer(4.0, 0.014, ("D5", "F5", "A5", "C6", "E6")), 8.4)
    place(bed, pad(["C2", "G2", "E3", "G3"], 8.0, 0.4, 0.7, 0.038), 12.4); place(bed, city(7.6, 0.022), 12.5)
    place(bed, pad(["A1", "E2", "C3", "E3"], 5.7, 0.4, 0.6, 0.042), 20.1); place(bed, shimmer(2.6, 0.018), 20.3); place(bed, room(3.0, 0.012), 22.7)
    place(bed, pad(["F2", "C3", "A3", "E4"], 7.3, 0.5, 0.7, 0.038), 25.5); place(bed, shimmer(6.8, 0.016, ("C5", "E5", "A5", "B5", "E6")), 25.7)
    place(bed, pad(["G1", "D2", "B2", "D3"], 6.5, 0.4, 0.6, 0.042), 32.5); place(bed, shimmer(6.0, 0.014), 32.7)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 7.3, 0.5, 2.0, 0.038), 38.7); place(bed, room(6.5, 0.01), 38.8); place(bed, shimmer(6.6, 0.016), 38.9)
    # effects
    place(fx, zap(0.07), 0.02); place(fx, boom(70, 0.7, 0.22), 0.03); place(fx, whoosh(0.6, 0.07), 3.05)
    place(fx, riser(2.3, 0.06), 3.8); place(fx, whir(2.4, 0.03), 3.8); place(fx, boom(80, 0.5, 0.22), 6.2); place(fx, beep(1800, 0.1, 0.03), 6.9); place(fx, beep(2525, 0.12, 0.03), 7.05)
    place(fx, whoosh(0.7, 0.09), 8.05); place(fx, whoosh(0.6, 0.09), 9.35); place(fx, boom(60, 0.5, 0.16), 9.6); place(fx, whoosh(0.6, 0.09), 10.75); place(fx, boom(60, 0.5, 0.16), 11.0)
    place(fx, whoosh(0.7, 0.09), 12.2); place(fx, boom(44, 1.2, 0.3), 12.5); place(fx, beep(1500, 0.1, 0.025), 14.1); place(fx, riser(1.4, 0.07), 15.7); place(fx, whoosh(0.9, 0.08), 16.2); place(fx, boom(70, 0.5, 0.18), 17.2)
    place(fx, whoosh(0.6, 0.08), 19.95); place(fx, boom(50, 0.9, 0.22), 20.2); place(fx, riser(1.9, 0.08), 20.7); place(fx, clicks(1.8, 30, 0.03, 2, 2500, 6000), 20.8)
    place(fx, boom(46, 1.3, 0.34), 22.7); place(fx, beep(2100, 0.14, 0.03), 23.7); place(fx, whoosh(0.6, 0.08), 25.35); place(fx, boom(55, 0.8, 0.2), 25.6)
    place(fx, riser(1.2, 0.04), 27.0); place(fx, boom(60, 0.6, 0.16), 28.1); place(fx, riser(1.3, 0.08), 29.9); place(fx, boom(48, 1.0, 0.3), 31.1); place(fx, zap(0.06), 31.15)
    place(fx, whoosh(0.6, 0.08), 32.35); place(fx, boom(52, 0.9, 0.3), 33.9); place(fx, zap(0.06), 33.9); place(fx, whoosh(0.5, 0.07), 35.1); place(fx, whoosh(0.6, 0.09), 35.85); place(fx, boom(50, 0.9, 0.28), 37.0); place(fx, zap(0.05), 37.0)
    place(fx, whoosh(0.6, 0.08), 38.55); place(fx, boom(60, 0.7, 0.18), 38.8); place(fx, riser(1.4, 0.04), 41.7)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/atoms.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
