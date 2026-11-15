"""Soundtrack + narration for the tunnel-through-the-Earth simulation. Writes work/tunnel.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 49.6
LINES = [(0.4, "What if you fell through a tunnel, to the other side of the Earth?"),
 (3.5, "You'd be weightless the whole way, and arrive in thirty eight minutes."),
 (7.2, "Picture a tunnel from pole to pole, with no air inside. You step off."),
 (12.0, "You fall faster and faster, but you feel no weight. You're in free fall."),
 (16.6, "Gravity stays strong almost halfway down. Then it fades."),
 (20.6, "At the centre, the Earth pulls you equally in every direction. Gravity is zero. But you're doing over twenty eight thousand kilometres an hour."),
 (29.4, "So you fly straight through, and gravity slows you down."),
 (33.2, "Thirty eight minutes after you stepped off, you rise out of the far side, and stop."),
 (38.2, "Grab the edge, or you fall all the way back."),
 (41.3, "No one can dig it: the deepest hole ever drilled is just twelve kilometres. But the physics is real."),
 (47.6, "Follow for more.")]
CHUNKS = [[], ["You'd be <em>weightless</em><br>the whole way,", "and arrive in<br><em>38 minutes</em>."],
 ["Picture a tunnel<br>from pole to pole,", "with <em>no air</em> inside.", "You step off."],
 ["You fall faster and faster,", "but you feel <em>no weight</em>.", "You're in free fall."],
 ["Gravity stays strong<br>almost <em>halfway</em> down.", "Then it fades."],
 ["At the centre, the Earth<br>pulls you equally", "in every direction.", "Gravity is <em>zero</em>.", "But you're doing over<br><em>28,000 km/h</em>."],
 ["So you fly<br>straight through,", "and gravity<br><em>slows you down</em>."],
 ["38 minutes after<br>you stepped off,", "you rise out of<br>the far side,", "and <em>stop</em>."],
 ["Grab the edge,", "or you fall<br><em>all the way back</em>."],
 ["No one can dig it:", "the deepest hole<br>ever drilled", "is just <em>12 kilometres</em>.", "But the physics is real."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(16)
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
    def tick(f=1100, lvl=0.12): t = np.arange(int(0.09 * SR)) / SR; return (np.sin(2 * np.pi * f * t) * np.exp(-t * 70) + rng.normal(0, .25, len(t)) * np.exp(-t * 500)) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * lvl
    def shimmer(d, lvl=0.022):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(["C5", "E5", "G5", "B5", "D6"])) * env(d, 0.8, 1.0) * lvl
    def wind(d, lvl=0.07):
        t = np.arange(int(d * SR)) / SR; x = bp(noise(d), 180, 900) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 3.7 + 1) ** 2) + bp(noise(d), 900, 2400) * 0.25 * (0.5 + 0.5 * np.sin(2 * np.pi * t / 2.3)); return x * lvl * env(d, 0.8, 0.8)
    def fall(d, f0, f1, lvl=0.09):   # rushing tunnel: band of noise whose pitch follows the speed
        m = int(d * SR); t = np.arange(m) / SR; x = noise(d); k = np.linspace(0, 1, m); lo = bp(x, 120, 700); hi = bp(x, 700, 4200)
        hum = np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, m)) / SR) * 0.25 + np.sin(2 * np.pi * np.cumsum(np.linspace(f0, f1, m) * 1.5) / SR) * 0.1
        return (lo * (1 - 0.5 * k if f1 > f0 else 0.5 + 0.5 * k) + hi * (0.25 + 0.75 * (k if f1 > f0 else 1 - k)) + hum) * lvl * env(d, 0.3, 0.3)
    def steps(d, lvl=0.05):
        out = np.zeros(int(d * SR)); t0 = 0.2
        while t0 < d - 0.2:
            tt = np.arange(int(0.12 * SR)) / SR; b = (bp(rng.normal(0, 1, len(tt)), 300, 2500) * np.exp(-tt * 45) + np.sin(2 * np.pi * 110 * tt) * np.exp(-tt * 30) * 0.6); i = int(t0 * SR); out[i:i + len(b)] += b; t0 += 0.42
        return out * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: space, polar wind, the fall, the diagram, the core, the rise, polar night, the ending
    place(bed, pad(["D2", "A2", "F3", "A3"], 7.2, 0.8, 0.8, 0.036), 0.0); place(bed, shimmer(7.0, 0.012), 0.1)
    place(bed, wind(4.8, 0.06), 6.9); place(bed, pad(["A2", "E3", "B3"], 4.8, 0.5, 0.4, 0.028), 6.9)
    place(bed, fall(5.0, 60, 150, 0.085), 11.5); place(bed, pad(["G2", "D3", "G3"], 5.0, 0.4, 0.4, 0.03), 11.5)
    place(bed, pad(["D2", "A2", "D3", "F3"], 8.8, 0.5, 0.8, 0.04), 16.3); place(bed, rumble(8.8, 0.035) * env(8.8, 1, 0.5), 16.3); place(bed, shimmer(8.6, 0.01), 16.4)
    place(bed, fall(4.4, 170, 180, 0.1), 24.9); place(bed, rumble(4.4, 0.06) * env(4.4, 0.2, 0.3), 24.9); place(bed, pad(["C2", "G2", "E3", "G3"], 4.4, 0.3, 0.4, 0.04), 24.9)
    place(bed, fall(4.0, 170, 55, 0.09), 29.1); place(bed, pad(["E2", "B2", "E3"], 4.0, 0.3, 0.4, 0.03), 29.1)
    place(bed, wind(8.3, 0.05), 32.9); place(bed, pad(["A2", "E3", "A3", "C4"], 8.3, 0.6, 0.8, 0.034), 32.9); place(bed, shimmer(8.0, 0.014), 33.0)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3"], 8.6, 0.5, 1.8, 0.04), 41.0); place(bed, shimmer(8.4, 0.012), 41.1)
    # effects
    for ts in [3.4, 7.0, 16.4, 41.1]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    place(fx, steps(2.9, 0.05), 7.3, pan=0.2); place(fx, riser(1.0, 0.05), 9.4); place(fx, whoosh(1.4, 0.11), 10.3); place(fx, boom(52, 1.4, 0.3), 11.6)
    place(fx, tick(820, 0.07), 18.6); place(fx, riser(1.8, 0.06), 20.6); place(fx, boom(40, 2.2, 0.45), 22.5); place(fx, boom(46, 2.0, 0.5), 25.0); place(fx, whoosh(1.2, 0.1), 25.6)
    place(fx, whoosh(0.8, 0.08), 29.1); place(fx, boom(50, 1.6, 0.35), 33.0); place(fx, whoosh(1.6, 0.07), 34.6); place(fx, tick(660, 0.1), 36.6); place(fx, tick(990, 0.1), 38.6); place(fx, tick(1100, 0.08), 39.1)
    place(fx, tick(900, 0.07), 42.8); place(fx, boom(60, 0.9, 0.2), 44.1)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/tunnel.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
