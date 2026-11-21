"""Soundtrack + narration for the all-the-ice-melted simulation. Writes work/ice.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 50.4
LINES = [(0.4, "What if all the ice on Earth melted?"),
 (2.6, "You're on the waterfront of a coastal city. The sea wouldn't come as a wave. It would come slowly. And it would not stop."),
 (9.6, "Start with the ice already floating in the sea. Melt all of it, and the water barely rises. Like ice cubes melting in a full glass."),
 (17.8, "The ice that matters sits on land. Mountain glaciers, Greenland, and above all, Antarctica."),
 (23.7, "Melt all of that, and the sea rises by around sixty to seventy metres. About as high as a twenty storey building."),
 (30.9, "Coastal cities all over the world go under. The map of every coast is redrawn."),
 (36.1, "But not overnight. At today's pace, about three millimetres a year, it would take more than twenty thousand years."),
 (42.6, "The ice won't vanish in a day. But every centimetre it gives up, the ocean keeps."),
 (47.9, "Follow for more.")]
CHUNKS = [[], ["You're on the waterfront<br>of a coastal city.", "The sea wouldn't come<br>as a <em>wave</em>.", "It would come <em>slowly</em>.", "And it would not stop."],
 ["Start with the ice already<br><em>floating</em> in the sea.", "Melt all of it,", "and the water <em>barely rises</em>.", "Like ice cubes melting<br>in a full glass."],
 ["The ice that matters<br>sits on <em>land</em>.", "Mountain glaciers, Greenland,", "and above all, <em>Antarctica</em>."],
 ["Melt all of that,", "and the sea rises by around<br><em>60 to 70 metres</em>.", "About as high as<br>a <em>20-storey</em> building."],
 ["Coastal cities all over<br>the world go under.", "The map of every coast<br>is <em>redrawn</em>."],
 ["But not overnight.", "At today's pace,<br>about <em>3 millimetres</em> a year,", "it would take more than<br><em>20,000 years</em>."],
 ["The ice won't vanish in a day.", "But every centimetre it gives up,", "the ocean <em>keeps</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(23)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def surf(d, lvl=0.05, per=5.3):
        t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 250, 2600); sw = 0.45 + 0.55 * np.sin(2 * np.pi * t / per - 1) ** 2; return x * sw * lvl * env(d, 0.6, 0.6)
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def bell(f=880, d=2.2, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.8) * lvl
    def creak(d=0.6, lvl=0.02):
        m = int(d * SR); t = np.arange(m) / SR; f = 180 + 60 * np.sin(2 * np.pi * 2.2 * t); return np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * lp(noise(d), 900) * np.sin(np.pi * t / d) ** 2 * lvl
    def gulls(d, lvl=0.02, seed=5):
        r = np.random.default_rng(seed); out = np.zeros(int(d * SR)); t0 = 0.4
        while t0 < d - 0.6:
            for j in range(r.integers(2, 4)):
                dd = r.uniform(0.18, 0.3); m = int(dd * SR); tt = np.arange(m) / SR; f = r.uniform(1500, 2100) * (1 + 0.35 * np.sin(np.pi * tt / dd)); ch = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / dd) ** 2; a = int((t0 + j * 0.33) * SR)
                if a + m < len(out): out[a:a + m] += ch * r.uniform(0.4, 1)
            t0 += r.uniform(1.4, 3.0)
        return out * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: waterfront, the glass, the globe, the rising sea, the drowned city, dusk
    place(bed, surf(9.6, 0.05), 0.0); place(bed, gulls(8.0, 0.016, 4), 0.6, pan=0.3); place(bed, pad(["A2", "E3", "A3", "C4"], 9.6, 1.0, 0.8, 0.032), 0.0)
    place(bed, pad(["D2", "A2", "F3", "C4"], 8.4, 0.5, 0.6, 0.036), 9.3); place(bed, shimmer(7.8, 0.014), 9.5)
    for ts in [10.4, 11.9, 13.1, 14.6, 15.8]: place(bed, tick(1900, 0.03), ts, pan=0.2); 
    place(bed, pad(["E2", "B2", "E3", "G3"], 6.1, 0.5, 0.5, 0.038), 17.5); place(bed, shimmer(5.6, 0.013, ("E5", "G5", "B5", "D6")), 17.6)
    place(bed, surf(12.6, 0.06, 3.1), 23.4); place(bed, rumble(12.4, 0.035) * env(12.4, 2.0, 1.5), 23.5); place(bed, pad(["C2", "G2", "E3", "B3"], 12.6, 0.6, 0.8, 0.04), 23.4)
    place(bed, surf(6.7, 0.045), 35.8); place(bed, pad(["F2", "C3", "A3", "E4"], 6.7, 0.5, 0.6, 0.036), 35.8)
    place(bed, surf(8.0, 0.05), 42.3); place(bed, gulls(5.0, 0.014, 8), 42.8, pan=-0.2); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 8.0, 0.5, 1.8, 0.034), 42.3)
    # effects
    for ts in [9.4, 17.6, 23.5, 30.7, 35.9, 42.4]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    place(fx, bell(990, 2.0, 0.025), 14.8); place(fx, boom(52, 1.0, 0.2), 17.6); place(fx, boom(50, 1.0, 0.18), 20.4)
    place(fx, riser(1.4, 0.05), 22.2); place(fx, boom(40, 2.6, 0.45), 23.5); place(fx, boom(44, 1.6, 0.25), 30.7); place(fx, boom(48, 1.0, 0.18), 35.9); place(fx, riser(1.2, 0.05), 41.3)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/ice.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
