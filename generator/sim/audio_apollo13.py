"""Soundtrack + narration for the Apollo 13 simulation. Writes work/apollo13.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 52.0
LINES = [(0.4, "Apollo thirteen, second by second."),
 (2.9, "April, nineteen seventy. Three astronauts are three hundred and twenty thousand kilometres from Earth. One routine switch will nearly kill them."),
 (11.8, "Mission control asks them to stir the oxygen tanks."),
 (15.0, "The fans switch on. Inside tank two, damaged wires spark. The insulation starts to burn."),
 (20.9, "For ninety three seconds, nobody knows. The pressure climbs."),
 (24.6, "Then, a bang. The tank bursts. Houston, we've had a problem."),
 (28.2, "Their oxygen is leaking into space. Without it, the fuel cells that power the ship will die."),
 (33.9, "So they move into the lunar lander. Built for two men, for two days. It has to keep three alive, for four."),
 (40.3, "They swing around the Moon. And on April seventeenth, they splash down, safe."),
 (44.8, "They never walked on the Moon. The lander that never landed, kept them alive."), (49.1, "Follow for more.")]
CHUNKS = [[], ["April, <em>1970</em>.", "Three astronauts are", "<em>320,000 kilometres</em><br>from Earth.", "One routine switch", "will nearly <em>kill</em> them."],
 ["Mission control asks them", "to <em>stir</em> the oxygen tanks."],
 ["The fans switch on.", "Inside tank two,", "damaged wires <em>spark</em>.", "The insulation<br>starts to <em>burn</em>."],
 ["For <em>ninety-three seconds</em>,", "nobody knows.", "The pressure climbs."],
 ["Then, a <em>bang</em>.", "The tank bursts.", "“Houston, we've had<br>a problem.”"],
 ["Their <em>oxygen</em> is leaking<br>into space.", "Without it, the fuel cells", "that power the ship<br>will die."],
 ["So they move into<br>the <em>lunar lander</em>.", "Built for two men,<br>for two days.", "It has to keep<br><em>three</em> alive,", "for <em>four</em>."],
 ["They swing around<br>the Moon.", "And on April seventeenth,", "they splash down, <em>safe</em>."],
 ["They never walked<br>on the Moon.", "The lander that<br>never landed", "kept them <em>alive</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(13)
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
    # beds: the hush of deep space, the control room, the tank, alarm, the long way home, the sea
    place(bed, pad(["D2", "A2", "D3", "F3"], 12.2, 1.2, 0.8, 0.04), 0.0); place(bed, shimmer(11.6, 0.014), 0.2)
    place(bed, pad(["C2", "G2", "E3"], 3.6, 0.3, 0.5, 0.034), 11.7); place(bed, radio(3.2), 11.8)
    place(bed, pad(["B1", "F2", "D3"], 6.3, 0.5, 0.6, 0.04), 14.9); place(bed, whir(9.2, 0.03), 15.9)
    place(bed, pad(["A1", "E2", "C3"], 4.4, 0.4, 0.2, 0.046), 20.8); place(bed, rumble(4.2, 0.05) * env(4.2, 3.3, 0.1), 20.9)
    place(bed, pad(["E2", "B2", "G3"], 9.1, 0.3, 0.8, 0.036), 25.1); place(bed, klaxon(5.4, 0.022), 26.6)
    place(bed, pad(["F2", "C3", "A3", "E4"], 6.6, 0.5, 0.8, 0.04), 33.8)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3"], 4.8, 0.5, 0.8, 0.04), 40.2); place(bed, shimmer(4.4, 0.016), 40.3)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 7.4, 0.5, 2.0, 0.038), 44.7); place(bed, shimmer(7.0, 0.016), 44.8)
    # effects
    place(fx, whoosh(0.6, 0.07), 2.65); place(fx, whoosh(0.5, 0.06), 7.35); place(fx, whoosh(0.5, 0.06), 11.55); place(fx, beep(), 11.85); place(fx, beep(2475), 14.5)
    place(fx, whoosh(0.5, 0.06), 14.75); place(fx, boom(70, 0.4, 0.2), 15.9); place(fx, whoosh(0.5, 0.06), 16.15)
    place(fx, clicks(3.6, 22, 0.07, 1, 2500, 6000), 17.3); place(fx, hiss(7.0, 0.035, 2.5, 0.1), 18.1)
    place(fx, riser(4.1, 0.11), 21.0); place(fx, boom(38, 3.2, 0.75), 25.1); place(fx, boom(90, 0.5, 0.4), 25.12); place(fx, hiss(2.6, 0.2, 0.02, 2.2), 25.15)
    place(fx, beep(), 26.25); place(fx, radio(1.6, 0.014), 26.3); place(fx, hiss(5.6, 0.06, 0.4, 1.0), 28.2); place(fx, whoosh(0.5, 0.06), 27.95)
    place(fx, whoosh(0.6, 0.07), 33.65); place(fx, boom(60, 0.6, 0.18), 35.3); place(fx, beep(1800, 0.12, 0.03), 36.0)
    place(fx, whoosh(0.6, 0.08), 40.05); place(fx, whoosh(0.7, 0.09), 42.05); place(fx, rumble(1.9, 0.04) * env(1.9, 0.2, 0.3), 42.3); place(fx, splash(0.3), 44.0); place(fx, boom(55, 0.8, 0.3), 44.0)
    place(fx, whoosh(0.6, 0.07), 44.55); place(fx, riser(1.4, 0.04), 47.4)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/apollo13.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
