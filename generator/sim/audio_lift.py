"""Soundtrack + narration for the lift-cable simulation. Writes work/lift.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 47.6
LINES = [(0.4, "What if the lift cable snapped?"),
 (2.3, "You're two hundred metres up when the cable snaps. In the movies, you'd hit the bottom at over two hundred kilometres an hour."),
 (9.2, "In real life, you'd barely move. Here's why."),
 (11.8, "A lift doesn't hang from one cable. It hangs from several steel ropes, far more than it needs."),
 (17.4, "And if they all failed, a governor would feel the car speeding up, and trip steel jaws that clamp onto the rails."),
 (23.8, "Elisha Otis proved it in the eighteen fifties. He stood on a platform, had the rope cut, and dropped just a few inches."),
 (30.9, "The one famous fall was in nineteen forty-five. A plane hit the Empire State Building, and cut the ropes and the brake line too. The car fell seventy-five floors. The operator lived."),
 (42.5, "The safety brake came first. Skyscrapers came after."), (46.0, "Follow for more.")]
CHUNKS = [[], ["You're <em>200 metres</em> up", "when the cable <em>snaps</em>.", "In the movies,", "you'd hit the bottom", "at over <em>200 km/h</em>."],
 ["In real life,<br>you'd <em>barely move</em>.", "Here's why."],
 ["A lift doesn't hang<br>from <em>one</em> cable.", "It hangs from several<br><em>steel ropes</em>,", "far more than it needs."],
 ["And if they <em>all</em> failed,", "a <em>governor</em> would feel<br>the car speeding up,", "and trip <em>steel jaws</em>", "that clamp onto the rails."],
 ["<em>Elisha Otis</em> proved it<br>in the 1850s.", "He stood on a platform,", "had the rope <em>cut</em>,", "and dropped just<br>a <em>few inches</em>."],
 ["The one famous fall<br>was in <em>1945</em>.", "A plane hit the<br>Empire State Building,", "and cut the ropes and<br>the <em>brake line</em> too.", "The car fell<br><em>75 floors</em>.", "The operator <em>lived</em>."],
 ["The <em>safety brake</em><br>came first.", "Skyscrapers came after."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(24)
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
    def room(d, lvl=0.012): return (lp(noise(d), 160, 2) * 2 + np.sin(2 * np.pi * 50 * np.arange(int(d * SR)) / SR) * 0.35) * env(d, 0.5, 0.5) * lvl
    def city(d, lvl=0.03): return (lp(noise(d), 300, 2) * 2.2 + bp(noise(d), 300, 1500) * 0.25) * env(d, 0.6, 1.2) * lvl
    def crowd(d, lvl=0.02): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 250, 1800) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.7 * t) ** 2) * env(d, 0.6, 0.6) * lvl
    def whir(d, lvl=0.04, f0=60, f1=220):
        t = np.arange(int(d * SR)) / SR; f = f0 + (f1 - f0) * np.minimum(1, t / d); return (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(2 * np.pi * np.cumsum(f * 3) / SR)) * env(d, 0.2, 0.2) * lvl
    def rumble(d, lvl=0.3): return (lp(noise(d), 70, 4) * 3 + bp(noise(d), 80, 320) * 0.5) * env(d, 0.1, 0.3) * lvl
    def wind(d, lvl=0.05, f0=300, f1=1800): t = np.arange(int(d * SR)) / SR; return bp(noise(d), f0, f1) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.31 * t + 1) ** 2) * env(d, 0.5, 0.5) * lvl
    def ting(f=3100, d=0.5, lvl=0.07): t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) + 0.3 * np.sin(2 * np.pi * f * 5.4 * t)) * np.exp(-t * 11) * lvl
    def crack(lvl=0.2): d = 0.5; t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 700, 6000) * np.exp(-t * 16) + lp(noise(d), 160) * np.exp(-t * 6) * 2) * lvl
    def twang(f=180, lvl=0.14): d = 0.9; t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f * (1 + 1.5 * np.exp(-t * 9))) / SR) + 0.5 * np.sin(2 * np.pi * f * 2.7 * t)) * np.exp(-t * 6) * lvl + hp(noise(d), 3000) * np.exp(-t * 30) * lvl
    def screech(d, lvl=0.06): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 2200, 5200) * 0.8 + np.sin(2 * np.pi * np.cumsum(np.linspace(2600, 900, len(t))) / SR) * 0.5) * env(d, 0.03, d * 0.6) * lvl
    def fall(d, lvl=0.06): m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 300, 3000) * (t / d) ** 1.6 * env(d, 0.05, 0.05) * lvl + np.sin(2 * np.pi * np.cumsum(np.linspace(90, 240, m)) / SR) * (t / d) ** 2 * env(d, 0.05, 0.05) * lvl * 0.7
    def prop(d, lvl=0.05): m = int(d * SR); t = np.arange(m) / SR; return (np.sign(np.sin(2 * np.pi * 95 * t)) * 0.3 + np.sin(2 * np.pi * 47 * t) + lp(noise(d), 400) * 0.6) * (t / d) ** 2 * lvl
    def ding(lvl=0.05): return ting(1320, 0.9, lvl) + ting(1760, 0.9, lvl * 0.5)
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: skyline, in the car, the movie fall, the calm truth, ropes, governor, the hall, 1945, the pit, the ending
    place(bed, pad(["D2", "A2", "D3", "F3"], 4.8, 0.6, 0.6, 0.036), 0.0); place(bed, wind(2.4, 0.04), 0.0); place(bed, room(2.6, 0.02), 2.1); place(bed, shimmer(2.2, 0.014), 0.2)
    place(bed, pad(["C2", "G2", "Eb3", "Gb3"], 4.6, 0.2, 0.4, 0.046), 4.4); place(bed, fall(4.2, 0.1), 4.5)
    place(bed, pad(["F2", "C3", "A3", "E4"], 8.6, 0.5, 0.7, 0.034), 9.0); place(bed, room(8.4, 0.02), 9.1); place(bed, shimmer(8.0, 0.012, ("C5", "E5", "A5", "B5", "E6")), 9.3)
    place(bed, pad(["E2", "B2", "G3", "D4"], 6.7, 0.4, 0.6, 0.04), 17.2); place(bed, room(6.3, 0.02), 17.3)
    place(bed, pad(["G2", "D3", "B3", "E4"], 7.4, 0.5, 0.7, 0.034), 23.6); place(bed, crowd(7.0, 0.03), 23.7)
    place(bed, pad(["A1", "E2", "C3", "G3"], 6.2, 0.6, 0.5, 0.044), 30.7); place(bed, wind(5.8, 0.045, 200, 1200), 30.8)
    place(bed, pad(["C2", "G2", "Eb3", "Bb3"], 6.0, 0.2, 0.8, 0.044), 36.5); place(bed, fall(4.0, 0.09), 36.7)
    place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 5.6, 0.5, 2.0, 0.038), 42.2); place(bed, city(5.0, 0.025), 42.4); place(bed, shimmer(5.0, 0.016), 42.5)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, whir(2.0, 0.03, 80, 140), 0.2); place(fx, ding(0.05), 2.2); place(fx, whoosh(0.5, 0.06), 2.0)
    place(fx, twang(170, 0.2), 4.5); place(fx, crack(0.22), 4.5); place(fx, twang(230, 0.1), 4.62, pan=0.3); place(fx, riser(1.6, 0.06), 7.0); place(fx, boom(44, 0.9, 0.4), 8.7)
    place(fx, whoosh(0.5, 0.1), 8.75); place(fx, ding(0.05), 9.15)
    place(fx, whoosh(0.6, 0.07), 11.6); place(fx, twang(200, 0.18), 14.5); place(fx, crack(0.12), 14.5); place(fx, ting(900, 0.5, 0.03), 14.75)
    place(fx, whoosh(0.5, 0.07), 17.2); place(fx, twang(170, 0.2), 18.0); place(fx, crack(0.2), 18.0); place(fx, whir(2.3, 0.05, 50, 420), 18.2); place(fx, ting(2200, 0.3, 0.07), 20.3); place(fx, crack(0.14), 20.3)
    place(fx, screech(1.4, 0.08), 20.5); place(fx, boom(60, 0.6, 0.3), 21.9); place(fx, ting(700, 0.6, 0.04), 21.95)
    place(fx, whoosh(0.6, 0.08), 23.5); place(fx, boom(60, 0.5, 0.14), 23.7); place(fx, crack(0.2), 28.0); place(fx, twang(140, 0.12), 28.0); place(fx, boom(80, 0.4, 0.25), 28.06); place(fx, ting(1500, 0.25, 0.05), 28.1); place(fx, crowd(2.0, 0.07), 28.5)
    place(fx, whoosh(0.6, 0.08), 30.6); place(fx, prop(4.4, 0.07), 30.9); place(fx, boom(40, 2.0, 0.6), 35.3); place(fx, crack(0.3), 35.3); place(fx, rumble(1.3, 0.2), 35.4)
    place(fx, whoosh(0.5, 0.09), 36.5); place(fx, twang(160, 0.14), 36.7); place(fx, screech(0.5, 0.03), 40.2); place(fx, boom(46, 1.4, 0.5), 40.7); place(fx, crack(0.24), 40.7); place(fx, ting(500, 0.8, 0.04), 40.9)
    place(fx, whoosh(0.6, 0.08), 42.2); place(fx, ding(0.05), 42.5); place(fx, whir(3.0, 0.02, 90, 130), 42.6); place(fx, riser(1.2, 0.04), 44.5)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/lift.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
