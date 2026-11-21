"""Soundtrack + narration for the Earth-crushed-into-a-black-hole simulation. Writes work/blackhole.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 48.0
LINES = [(0.4, "What if the Earth were crushed into a black hole?"),
 (3.3, "It would be the size of a marble. And the Moon wouldn't even notice."),
 (7.4, "Every black hole has a size set by its mass. For the Earth, that's a ball under two centimetres across."),
 (14.2, "The whole planet, every mountain and every ocean, squeezed into that."),
 (18.5, "You'd expect it to swallow everything nearby. It wouldn't."),
 (22.2, "From far away, gravity only cares about mass. Same mass, same pull."),
 (27.1, "So the Moon keeps circling, once every twenty-seven days, around a speck too small to see."),
 (32.8, "Only up close does it turn deadly. One metre away, the pull is about forty trillion times what you feel now."),
 (40.1, "A black hole isn't a vacuum cleaner. It's just gravity, with nothing left to stand on."), (45.5, "Follow for more.")]
CHUNKS = [[], ["It would be the size<br>of a <em>marble</em>.", "And the Moon<br>wouldn't even <em>notice</em>."],
 ["Every black hole has a size", "set by its <em>mass</em>.", "For the Earth, that's a ball", "under <em>two centimetres</em><br>across."],
 ["The whole planet,", "every mountain<br>and every ocean,", "squeezed into <em>that</em>."],
 ["You'd expect it to swallow<br>everything nearby.", "It <em>wouldn't</em>."],
 ["From far away, gravity<br>only cares about <em>mass</em>.", "Same mass,", "<em>same pull</em>."],
 ["So the Moon keeps circling,", "once every<br><em>twenty-seven days</em>,", "around a speck<br>too small to see."],
 ["Only up close<br>does it turn <em>deadly</em>.", "One metre away,", "the pull is about<br><em>forty trillion times</em>", "what you feel now."],
 ["A black hole isn't<br>a <em>vacuum cleaner</em>.", "It's just gravity,", "with nothing left<br>to <em>stand on</em>."], []]
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
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def faller(d=2.4, lvl=0.1):
        """The crush: a tone that sinks while a rumble swells."""
        m = int(d * SR); t = np.arange(m) / SR; return (np.sin(2 * np.pi * np.cumsum(np.linspace(520, 38, m)) / SR) * 0.5 + lp(noise(d), 140, 4) * 2.4 * (t / d)) * (0.25 + 0.75 * (t / d) ** 1.5) * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def zap(lvl=0.1):
        d = 0.28; m = int(d * SR); t = np.arange(m) / SR; return (np.sin(2 * np.pi * np.cumsum(np.linspace(3200, 500, m)) / SR) * 0.6 + hp(noise(d), 3000) * 0.4) * np.exp(-t * 16) * lvl
    def park(d, lvl=0.02):
        """Daylight air with a few bird chirps."""
        x = (lp(noise(d), 400, 2) * 1.6 + bp(noise(d), 1500, 5000) * 0.12) * env(d, 0.3, 0.4) * lvl; r = np.random.default_rng(5); t0 = 0.25
        while t0 < d - 0.3:
            dd = 0.09; tt = np.arange(int(dd * SR)) / SR; f = r.uniform(2800, 4200); c = np.sin(2 * np.pi * (f * tt + 900 * tt ** 2 / dd)) * np.sin(np.pi * tt / dd) ** 2 * lvl * 0.9
            for k in range(int(r.integers(1, 4))): i = int((t0 + k * 0.13) * SR); x[i:i + len(c)] += c[: max(0, len(x) - i)]
            t0 += r.uniform(0.5, 1.1)
        return x
    def beep(f=2525, d=0.25, lvl=0.035): t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * f * t) * env(d, 0.005, 0.02) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def tick(lvl=0.03): t = np.arange(int(0.03 * SR)) / SR; return np.sin(2 * np.pi * 1900 * t) * np.exp(-t * 220) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: space, the park, the Moon's orbit, the crush, the palm, the wrong guess, the comparison, the Moon, one metre, the calm end
    place(bed, pad(["D2", "A2", "D3", "F3"], 3.4, 0.6, 0.6, 0.04), 0.0); place(bed, shimmer(3.0, 0.016), 0.1)
    place(bed, park(2.3, 0.022), 3.0); place(bed, pad(["F2", "C3", "A3"], 2.4, 0.3, 0.4, 0.034), 3.0)
    place(bed, pad(["D2", "A2", "E3", "A3"], 2.3, 0.3, 0.5, 0.038), 5.1); place(bed, shimmer(2.0, 0.014, ("D5", "F5", "A5", "C6", "E6")), 5.2)
    place(bed, pad(["B1", "F2", "D3"], 7.1, 0.5, 0.7, 0.044), 7.0); place(bed, rumble(4.6, 0.035) * env(4.6, 2.5, 0.2), 7.9)
    place(bed, park(4.5, 0.022), 13.9); place(bed, pad(["F2", "C3", "A3", "E4"], 4.6, 0.4, 0.5, 0.034), 13.9)
    place(bed, pad(["A1", "E2", "C3"], 4.0, 0.4, 0.4, 0.046), 18.1)
    place(bed, pad(["C2", "G2", "E3", "G3"], 5.2, 0.4, 0.6, 0.038), 21.8); place(bed, shimmer(4.6, 0.014), 22.0)
    place(bed, pad(["D2", "A2", "F3", "C4"], 6.0, 0.5, 0.7, 0.038), 26.7); place(bed, shimmer(5.4, 0.016, ("D5", "F5", "A5", "C6", "E6")), 26.9)
    place(bed, pad(["A1", "E2", "B2"], 7.6, 0.4, 0.3, 0.048), 32.4); place(bed, rumble(7.0, 0.03) * env(7.0, 3.0, 0.3), 32.6)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 8.3, 0.5, 2.0, 0.038), 39.7); place(bed, shimmer(7.6, 0.016), 39.9)
    # effects
    place(fx, boom(60, 0.8, 0.28), 0.03); place(fx, whoosh(0.6, 0.07), 2.85); place(fx, whoosh(0.6, 0.07), 4.95); place(fx, whoosh(0.6, 0.08), 6.95)
    place(fx, faller(2.4, 0.13), 10.0); place(fx, boom(38, 2.2, 0.75), 12.4); place(fx, zap(0.08), 12.4); place(fx, boom(90, 0.4, 0.3), 12.42)
    place(fx, whoosh(0.6, 0.07), 13.75); place(fx, whoosh(0.6, 0.07), 18.05); place(fx, riser(1.6, 0.05), 19.0); place(fx, beep(1400, 0.12, 0.035), 20.7); place(fx, beep(1050, 0.2, 0.035), 20.84)
    place(fx, whoosh(0.6, 0.07), 21.75); place(fx, boom(55, 0.5, 0.15), 25.0); place(fx, boom(55, 0.5, 0.15), 25.75); place(fx, whoosh(0.6, 0.07), 26.65)
    for k in range(10): place(fx, tick(0.03), 27.4 + k * 0.5)
    place(fx, whoosh(0.6, 0.08), 32.35); place(fx, boom(44, 1.2, 0.3), 32.6); place(fx, riser(2.6, 0.07), 36.1); place(fx, zap(0.12), 38.7); place(fx, boom(40, 1.6, 0.6), 38.72)
    place(fx, whoosh(0.6, 0.07), 39.65); place(fx, riser(1.4, 0.04), 43.9)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/blackhole.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
