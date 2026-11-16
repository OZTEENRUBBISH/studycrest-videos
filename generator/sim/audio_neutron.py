"""Soundtrack + narration for the teaspoon-of-neutron-star simulation. Writes work/neutron.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 46.0
LINES = [(0.4, "What if a teaspoon of neutron star appeared on your desk?"),
 (3.6, "You'd expect it to crash through the floor. It wouldn't. It would explode."),
 (7.6, "A neutron star is the core of a dead star. The mass of a Sun, crushed into a ball the size of a city."),
 (14.4, "One teaspoon of it weighs billions of tonnes. As much as a mountain."),
 (18.7, "But only the star's gravity keeps it squeezed that small."),
 (22.2, "On your desk, nothing holds it in. It bursts outward in an instant. A giant explosion, big enough to vaporise part of the planet."),
 (31.0, "And the neutrons? On their own, each one lasts about fifteen minutes, then decays into a proton."),
 (37.2, "Neutron star matter isn't something you can hold. It only exists while a star is crushing it."), (43.4, "Follow for more.")]
CHUNKS = [[], ["You'd expect it to crash<br>through the floor.", "It <em>wouldn't</em>.", "It would <em>explode</em>."],
 ["A neutron star is the core<br>of a <em>dead star</em>.", "The mass of a Sun,", "crushed into a ball", "the size of a <em>city</em>."],
 ["One teaspoon of it weighs<br><em>billions of tonnes</em>.", "As much as a <em>mountain</em>."],
 ["But only the star's <em>gravity</em>", "keeps it squeezed<br>that small."],
 ["On your desk,<br><em>nothing</em> holds it in.", "It bursts outward<br>in an instant.", "A <em>giant explosion</em>,", "big enough to vaporise<br>part of the planet."],
 ["And the neutrons?", "On their own, each one lasts", "about <em>fifteen minutes</em>,", "then decays<br>into a <em>proton</em>."],
 ["Neutron star matter isn't<br>something you can <em>hold</em>.", "It only exists while<br>a star is <em>crushing</em> it."], []]
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
    # beds: the quiet room, the star, the mountain air, gravity, the burst, one neutron, the star again
    place(bed, room(7.6, 0.014), 0.0); place(bed, pad(["D2", "A2", "D3", "F3"], 7.7, 0.8, 0.8, 0.036), 0.0); place(bed, shimmer(3.2, 0.014), 0.2)
    place(bed, pad(["B1", "F2", "D3", "A3"], 7.1, 0.5, 0.7, 0.042), 7.3); place(bed, shimmer(6.6, 0.016, ("D5", "F5", "A5", "C6", "E6")), 7.5); place(bed, whir(6.6, 0.014), 7.5)
    place(bed, pad(["C2", "G2", "E3", "G3"], 4.6, 0.4, 0.6, 0.038), 14.1); place(bed, city(4.2, 0.012), 14.2)
    place(bed, pad(["A1", "E2", "C3"], 3.8, 0.4, 0.4, 0.046), 18.4); place(bed, rumble(3.4, 0.03) * env(3.4, 0.6, 0.4), 18.5)
    place(bed, room(2.9, 0.014), 22.0); place(bed, pad(["A1", "E2", "B2"], 3.0, 0.3, 0.1, 0.044), 22.0)
    place(bed, pad(["D2", "A2", "D3", "F3"], 6.2, 0.2, 0.8, 0.042), 24.9); place(bed, rumble(5.8, 0.09) * env(5.8, 0.05, 2.5), 24.9)
    place(bed, pad(["F2", "C3", "A3", "E4"], 6.5, 0.5, 0.7, 0.036), 30.7); place(bed, shimmer(6.0, 0.014), 30.9)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 9.0, 0.5, 2.0, 0.038), 36.9); place(bed, shimmer(8.4, 0.016), 37.0)
    # effects
    place(fx, zap(0.09), 0.02); place(fx, boom(70, 0.7, 0.25), 0.03); place(fx, whoosh(0.6, 0.07), 3.15)
    place(fx, boom(55, 0.5, 0.16), 4.4); place(fx, beep(1800, 0.1, 0.03), 5.7); place(fx, riser(1.0, 0.05), 6.0); place(fx, boom(60, 0.8, 0.3), 6.9)
    place(fx, whoosh(0.6, 0.08), 7.15); place(fx, boom(44, 1.4, 0.3), 7.4); place(fx, whoosh(0.5, 0.05), 10.3); place(fx, boom(60, 0.5, 0.14), 11.1)
    place(fx, whoosh(0.6, 0.07), 13.95); place(fx, boom(50, 0.9, 0.22), 16.4); place(fx, whoosh(0.6, 0.07), 18.25)
    place(fx, whoosh(0.6, 0.07), 21.75); place(fx, clicks(1.7, 16, 0.05, 2, 2500, 6000), 23.2); place(fx, riser(1.7, 0.12), 23.2)
    place(fx, boom(36, 3.6, 0.8), 24.9); place(fx, boom(90, 0.5, 0.4), 24.92); place(fx, hiss(2.4, 0.16, 0.02, 2.0), 24.95); place(fx, boom(42, 2.6, 0.5), 25.7); place(fx, boom(40, 2.8, 0.45), 27.5)
    place(fx, whoosh(0.6, 0.07), 30.55); place(fx, clicks(3.4, 5, 0.05, 4, 1500, 2600), 31.2); place(fx, zap(0.08), 34.6); place(fx, boom(80, 0.5, 0.2), 34.6)
    place(fx, whoosh(0.6, 0.07), 36.75); place(fx, riser(1.4, 0.04), 41.7)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/neutron.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
