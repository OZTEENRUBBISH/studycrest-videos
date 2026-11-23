"""Soundtrack + narration for the deepest-ocean simulation. Writes work/ocean.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 47.8
LINES = [(0.4, "What if you sank to the deepest point in the ocean?"),
 (2.9, "You're floating in the Pacific, with almost eleven kilometres of water below you. People say the pressure would crush you flat. It wouldn't."),
 (11.1, "Every ten metres down adds another atmosphere. At just ten metres, the air in your lungs is squeezed to half its size."),
 (18.3, "By two hundred metres, the sunlight is fading. By a thousand, it's gone."),
 (22.8, "At the bottom, more than a tonne presses on every square centimetre."),
 (26.8, "Your lungs, sinuses and ears would collapse, because air squeezes easily. You would not survive."),
 (32.6, "But water hardly squeezes at all, and you are mostly water. The rest of you would keep its shape."),
 (38.3, "That's how a snailfish lives eight kilometres down. It has no air inside to crush."),
 (43.4, "Pressure doesn't crush water. It crushes air."), (46.2, "Follow for more.")]
CHUNKS = [[], ["You're floating<br>in the <em>Pacific</em>,", "with almost <em>11 kilometres</em><br>of water below you.", "People say the pressure", "would <em>crush you flat</em>.", "It <em>wouldn't</em>."],
 ["Every <em>10 metres</em> down", "adds another <em>atmosphere</em>.", "At just 10 metres,", "the air in your lungs", "is squeezed to<br><em>half its size</em>."],
 ["By <em>200 metres</em>,", "the sunlight is fading.", "By a <em>thousand</em>,", "it's <em>gone</em>."],
 ["At the bottom,", "more than <em>a tonne</em>", "presses on every<br><em>square centimetre</em>."],
 ["Your lungs, sinuses<br>and ears would <em>collapse</em>,", "because <em>air</em><br>squeezes easily.", "You would not survive."],
 ["But <em>water</em> hardly<br>squeezes at all,", "and you are<br><em>mostly water</em>.", "The rest of you", "would <em>keep its shape</em>."],
 ["That's how a <em>snailfish</em>", "lives <em>8 kilometres</em> down.", "It has no air inside<br>to crush."],
 ["Pressure doesn't<br>crush <em>water</em>.", "It crushes <em>air</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(31)
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
    def ting(f=3100, d=0.5, lvl=0.07): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 11) * lvl
    def ding(lvl=0.05): return ting(1320, 0.9, lvl) + ting(1760, 0.9, lvl * 0.5)
    def waves(d, lvl=0.05): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 300, 2600) * (0.35 + 0.65 * np.sin(2 * np.pi * 0.21 * t) ** 2) + lp(noise(d), 200) * 0.8) * env(d, 0.5, 0.6) * lvl
    def gull(lvl=0.03): d = 0.45; t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * np.cumsum(2300 - 900 * (t / d) + 250 * np.sin(2 * np.pi * 9 * t)) / SR) * np.sin(np.pi * t / d) ** 2 * lvl
    def deep(d, lvl=0.05, f=180): t = np.arange(int(d * SR)) / SR; return (lp(noise(d), f, 4) * 3 + np.sin(2 * np.pi * 41 * t) * 0.25 * (1 + 0.5 * np.sin(2 * np.pi * 0.13 * t))) * env(d, 0.6, 0.8) * lvl
    def bubbles(d, lvl=0.05, rate=9):
        m = int(d * SR); x = np.zeros(m)
        for _ in range(int(d * rate)):
            i = int(rng.uniform(0, m - 4000)); L = int(rng.uniform(0.03, 0.09) * SR); t = np.arange(L) / SR; f0 = rng.uniform(380, 1500)
            x[i:i + L] += np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.6 * t / t[-1])) / SR) * np.sin(np.pi * t / t[-1]) ** 2 * rng.uniform(0.3, 1)
        return lp(x, 3000) * env(d, 0.1, 0.5) * lvl
    def splash(lvl=0.12): d = 1.1; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 400, 5000) * np.exp(-t * 5) + lp(noise(d), 250) * np.exp(-t * 3) * 1.5) * lvl
    def sonar(lvl=0.05, f=1180): d = 1.6; t = np.arange(int(d * SR)) / SR; x = np.sin(2 * np.pi * f * t) * np.exp(-t * 4) * lvl; e = np.zeros_like(x); k = int(0.33 * SR); e[k:] = x[:-k] * 0.35; return x + e
    def creak(lvl=0.08, d=1.2): m = int(d * SR); t = np.arange(m) / SR; return (np.sign(np.sin(2 * np.pi * np.cumsum(np.linspace(58, 34, m)) / SR)) * 0.3 + lp(noise(d), 120, 3) * 2) * env(d, 0.15, 0.6) * lvl
    def squeeze(d=1.4, lvl=0.06): m = int(d * SR); t = np.arange(m) / SR; return np.sin(2 * np.pi * np.cumsum(np.linspace(700, 190, m)) / SR) * env(d, 0.05, 0.4) * lvl + bubbles(d, lvl * 0.8, 14)
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the surface, the myth, the first ten metres, the twilight, the bottom, the air spaces, the experiment, the snailfish, the surface again
    place(bed, pad(["D2", "A2", "F#3", "A3"], 7.4, 0.6, 0.6, 0.032), 0.0); place(bed, waves(7.0, 0.07), 0.0); place(bed, shimmer(6.6, 0.014), 0.2)
    place(bed, pad(["C2", "G2", "Eb3", "Gb3"], 3.2, 0.2, 0.3, 0.046), 7.0); place(bed, deep(3.0, 0.06), 7.0)
    place(bed, pad(["F2", "C3", "A3", "E4"], 8.6, 0.5, 0.7, 0.032), 10.0); place(bed, deep(8.3, 0.035, 320), 10.1); place(bed, bubbles(7.0, 0.035, 7), 11.0); place(bed, shimmer(7.0, 0.01, ("C5", "E5", "A5", "B5", "E6")), 10.6)
    place(bed, pad(["D2", "A2", "D3", "F3"], 4.8, 0.4, 0.6, 0.04), 18.1); place(bed, deep(4.6, 0.05, 220), 18.2)
    place(bed, pad(["A1", "E2", "C3", "G3"], 10.2, 0.6, 0.6, 0.044), 22.5); place(bed, deep(10.0, 0.065, 140), 22.6)
    place(bed, pad(["G2", "D3", "B3", "E4"], 6.0, 0.5, 0.7, 0.032), 32.3); place(bed, deep(5.8, 0.045, 200), 32.4); place(bed, shimmer(5.4, 0.012), 32.6)
    place(bed, pad(["E2", "B2", "G3", "D4", "F#4"], 5.4, 0.5, 0.7, 0.036), 38.0); place(bed, deep(5.2, 0.05, 160), 38.1); place(bed, shimmer(5.0, 0.014, ("B4", "E5", "G5", "B5", "D6")), 38.2)
    place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 4.8, 0.4, 2.0, 0.038), 43.1); place(bed, waves(4.6, 0.06), 43.2); place(bed, shimmer(4.4, 0.016), 43.3)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, gull(0.03), 0.9, pan=-0.4); place(fx, gull(0.022), 1.5, pan=0.5); place(fx, whoosh(0.5, 0.06), 2.6); place(fx, gull(0.02), 4.6, pan=0.3); place(fx, sonar(0.04), 5.6)
    place(fx, whoosh(0.5, 0.1), 7.05); place(fx, boom(44, 1.0, 0.4), 7.15); place(fx, creak(0.1), 7.7); place(fx, squeeze(1.5, 0.06), 8.2); place(fx, riser(1.0, 0.05), 8.55)
    place(fx, boom(52, 0.8, 0.36), 9.6); place(fx, ding(0.05), 9.7)
    place(fx, whoosh(0.5, 0.08), 10.9); place(fx, splash(0.14), 11.0); place(fx, bubbles(1.6, 0.09, 16), 11.1); place(fx, ting(900, 0.5, 0.03), 14.2); place(fx, squeeze(1.8, 0.05), 15.6); place(fx, ding(0.04), 17.6)
    place(fx, whoosh(0.6, 0.08), 18.1); place(fx, sonar(0.04, 980), 19.0); place(fx, riser(1.4, 0.04), 20.4); place(fx, boom(40, 1.2, 0.3), 21.5); place(fx, sonar(0.03, 760), 21.6)
    place(fx, whoosh(0.6, 0.09), 22.5); place(fx, boom(38, 1.8, 0.5), 24.6); place(fx, creak(0.07, 1.6), 24.9); place(fx, ting(500, 0.8, 0.03), 25.4)
    place(fx, whoosh(0.5, 0.07), 26.5); place(fx, squeeze(2.4, 0.06), 27.4); place(fx, boom(46, 1.0, 0.25), 29.9); place(fx, ting(420, 1.2, 0.03), 30.9)
    place(fx, whoosh(0.6, 0.08), 32.3); place(fx, squeeze(2.0, 0.045), 33.0); place(fx, ding(0.045), 34.9); place(fx, whoosh(0.5, 0.07), 35.1); place(fx, boom(50, 0.8, 0.2), 35.3)
    place(fx, whoosh(0.6, 0.08), 38.0); place(fx, sonar(0.035, 1320), 38.5); place(fx, bubbles(1.0, 0.03, 5), 40.6); place(fx, ding(0.04), 41.4)
    place(fx, whoosh(0.7, 0.09), 43.1); place(fx, splash(0.1), 43.2); place(fx, gull(0.025), 43.9, pan=-0.3); place(fx, ding(0.05), 43.5); place(fx, gull(0.02), 45.2, pan=0.4); place(fx, riser(1.0, 0.035), 45.2)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/ocean.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
