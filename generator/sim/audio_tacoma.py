"""Soundtrack + narration for the Tacoma Narrows Bridge simulation. Writes work/tacoma.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 57.6
LINES = [(0.4, "Tacoma Narrows Bridge, minute by minute."),
 (2.7, "In nineteen forty, this bridge tore itself apart. The wind didn't knock it down. Its own twisting did."),
 (9.0, "November seventh. The bridge is four months old, and has bounced since opening day. Locals call it Galloping Gertie."),
 (15.7, "This morning, the wind blows at about sixty eight kilometres an hour."),
 (19.8, "Ten oh three a.m. The bouncing turns into a twist. The road tilts up to forty five degrees, one way, then the other, every five seconds."),
 (28.7, "For years, textbooks blamed resonance. Engineers now call it flutter: each twist changes the airflow, and the airflow twists it further."),
 (38.2, "Eleven oh two. About a hundred and eighty metres of road breaks free and falls."),
 (44.9, "No person died. A dog named Tubby, trapped in a car, was the only life lost."),
 (49.9, "Today, wind tunnel tests for bridges are routine."),
 (52.9, "The wind didn't knock it down. The twist fed itself."),
 (55.9, "Follow for more.")]
CHUNKS = [[], ["In <em>1940</em>, this bridge", "<em>tore itself apart</em>.", "The wind didn't<br>knock it down.", "Its own <em>twisting</em> did."],
 ["November 7th.", "The bridge is<br><em>four months old</em>,", "and has <em>bounced</em><br>since opening day.", "Locals call it<br><em>Galloping Gertie</em>."],
 ["This morning,<br>the wind blows", "at about<br><em>68 kilometres an hour</em>."],
 ["10:03 a.m.", "The bouncing turns<br>into a <em>twist</em>.", "The road tilts<br>up to <em>45 degrees</em>,", "one way, then the other,", "every <em>five seconds</em>."],
 ["For years, textbooks<br>blamed <em>resonance</em>.", "Engineers now call it<br><em>flutter</em>:", "each twist changes<br>the airflow,", "and the airflow<br><em>twists it further</em>."],
 ["11:02.", "About <em>180 metres</em><br>of road", "breaks free and falls."],
 ["<em>No person died.</em>", "A dog named Tubby,<br>trapped in a car,", "was the only life lost."],
 ["Today, <em>wind tunnel tests</em>", "for bridges are routine."],
 ["The wind didn't<br>knock it down.", "The twist <em>fed itself</em>."], []]
if __name__ == "__main__":
    from vo import speak, SR, BASE
    from soundlib import place, N
    n = int(DUR * SR); rng = np.random.default_rng(1940)
    def sos(kind, f, order=2): return signal.butter(order, f, kind, fs=SR, output="sos")
    def noise(d): return rng.normal(0, 1, int(d * SR))
    def lp(x, f, o=2): return signal.sosfilt(sos("lowpass", f, o), x)
    def hp(x, f, o=2): return signal.sosfilt(sos("highpass", f, o), x)
    def bp(x, a, b): return signal.sosfilt(sos("bandpass", [a, b]), x)
    def env(d, a, r, p=1.0): t = np.arange(int(d * SR)) / SR; return (np.minimum(1, t / max(a, 1e-4)) * np.minimum(1, (d - t) / max(r, 1e-4)).clip(0)) ** p
    def pad(notes, d, a=1.2, r=1.5, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; x = sum(np.sin(2 * np.pi * N(nm) * t + k * 1.3) + 0.3 * np.sin(2 * np.pi * N(nm) * 2.003 * t + k) + 0.12 * np.sin(2 * np.pi * N(nm) * 3.01 * t) for k, nm in enumerate(notes))
        return x * env(d, a, r) * lvl * (1 + 0.1 * np.sin(2 * np.pi * 0.27 * t))
    def wind(d, lvl=0.04, gust=0.17):
        t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 180, 1300) + 0.5 * bp(noise(d), 900, 3200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.41 * t))) * (0.55 + 0.45 * np.sin(2 * np.pi * gust * t + 1) ** 2) * lvl * env(d, 0.6, 0.6)
    def boom(f=46, d=1.8, lvl=0.5):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * np.cumsum(f + 70 * np.exp(-t * 14)) / SR) * np.exp(-t * 2.6) + lp(noise(d), 180) * np.exp(-t * 7) * 0.5) * lvl
    def whoosh(d=0.7, lvl=0.09):
        m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 500, 6000) * 0.6 * np.sin(np.pi * t / d) ** 2 * lvl
    def riser(d=2.0, lvl=0.07):
        m = int(d * SR); t = np.arange(m) / SR; return (hp(noise(d), 1500) * 0.5 + np.sin(2 * np.pi * np.cumsum(np.linspace(180, 900, m)) / SR) * 0.4) * (t / d) ** 2.2 * lvl
    def shimmer(d, lvl=0.022, notes=("C5", "E5", "G5", "B5", "D6")):
        t = np.arange(int(d * SR)) / SR; return sum(np.sin(2 * np.pi * N(nm) * t * (1 + 0.002 * np.sin(2 * np.pi * (0.3 + k * 0.11) * t))) for k, nm in enumerate(notes)) * env(d, 0.8, 1.0) * lvl
    def groan(d=2.4, f0=70, lvl=0.16):   # steel under strain: a slow bending tone with a rasp
        m = int(d * SR); t = np.arange(m) / SR; f = f0 * (1 + 0.35 * np.sin(np.pi * t / d)); ph = 2 * np.pi * np.cumsum(f) / SR
        x = np.sign(np.sin(ph)) * 0.25 + np.sin(ph) + 0.5 * np.sin(2.01 * ph) + 0.3 * np.sin(3.98 * ph); return (lp(x, 700) + bp(noise(d), 300, 1500) * 0.25 * np.abs(np.sin(ph * 0.25))) * np.sin(np.pi * t / d) ** 1.5 * lvl
    def snap(lvl=0.5): t = np.arange(int(0.5 * SR)) / SR; return (hp(noise(0.5), 1200) * np.exp(-t * 26) + np.sin(2 * np.pi * 190 * t) * np.exp(-t * 12) * 0.7) * lvl
    def crash(d=2.6, lvl=0.3): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 120, 2600) * np.exp(-t * 2.2) * (0.6 + 0.4 * np.abs(lp(noise(d), 18)) * 3) + lp(noise(d), 110, 3) * 3 * np.exp(-t * 1.6)) * lvl
    def splash(d=2.4, lvl=0.22): t = np.arange(int(d * SR)) / SR; return (bp(noise(d), 500, 7000) * np.minimum(1, t / 0.05) * np.exp(-t * 1.9) + lp(noise(d), 140, 3) * 2.5 * np.exp(-t * 5)) * lvl
    def water(d, lvl=0.02): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 300, 2400) * (0.4 + 0.6 * np.sin(2 * np.pi * 0.23 * t) ** 2) * lvl * env(d, 0.5, 0.5)
    def bell(f=880, d=2.2, lvl=0.03):
        t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 3) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 6)) * np.exp(-t * 1.8) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    T = dict(hook=2.5, hBreak=6.3, date=8.8, wind=15.5, twist=19.6, tw0=21.0, flutter=28.5, fall=38.0, brk=39.7, gone=42.5, toll=44.7, today=49.7, close=52.7, end=55.7)
    # beds: wind all the way through the morning, pads per scene, calm for the epilogue
    place(bed, wind(2.7, 0.03), 0.0); place(bed, pad(["D2", "A2", "F3", "A3"], 2.8, 0.4, 0.5, 0.034), 0.0)
    place(bed, wind(6.5, 0.055), 2.4); place(bed, pad(["C2", "G2", "Eb3", "Bb3"], 6.5, 0.3, 0.5, 0.042), 2.4)
    place(bed, wind(6.9, 0.035), 8.7); place(bed, water(6.7, 0.012), 8.8); place(bed, pad(["F2", "C3", "A3", "E4"], 6.9, 0.6, 0.6, 0.032), 8.7)
    place(bed, wind(4.3, 0.065, 0.3), 15.4); place(bed, pad(["D2", "A2", "F3", "C4"], 4.3, 0.4, 0.5, 0.036), 15.4)
    place(bed, wind(9.1, 0.055), 19.5); place(bed, pad(["C2", "G2", "Eb3", "G3"], 9.1, 0.4, 0.5, 0.044), 19.5)
    place(bed, wind(9.7, 0.045), 28.4); place(bed, pad(["Bb1", "F2", "Db3", "Ab3"], 9.7, 0.5, 0.6, 0.04), 28.4)
    place(bed, wind(6.9, 0.055), 37.9); place(bed, pad(["A1", "E2", "C3", "Eb3"], 6.9, 0.3, 0.5, 0.046), 37.9)
    place(bed, wind(5.2, 0.03), 44.6); place(bed, pad(["D2", "A2", "D3", "F3"], 5.2, 0.5, 0.8, 0.04), 44.6)
    place(bed, water(7.8, 0.012), 49.7); place(bed, pad(["D2", "A2", "D3", "F#3", "A3", "E4"], 7.9, 0.6, 2.2, 0.036), 49.6); place(bed, shimmer(5.4, 0.012, ("D5", "F#5", "A5", "C#6")), 50.0)
    # effects
    for ts in [T["hook"], T["hBreak"] - 0.6, T["date"], T["wind"], T["twist"], T["flutter"], T["fall"], T["toll"], T["today"]]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    # the twist: one groan every half cycle (2.5 s), louder as it grows
    for k in range(2): place(fx, groan(2.3, 62 + 8 * (k % 2), 0.13), 2.6 + k * 2.5 - 0.35, pan=(-0.4 if k % 2 else 0.4))
    place(fx, snap(0.45), T["hBreak"]); place(fx, crash(2.4, 0.3), T["hBreak"] + 0.05); place(fx, boom(40, 2.2, 0.5), T["hBreak"] + 0.05)
    for k in range(3): place(fx, groan(1.6, 48 + 5 * k, 0.05), 10.0 + k * 1.59)
    for k in range(7):
        ts = T["tw0"] + 1.25 + k * 2.5 - 1.15
        if ts < T["fall"] - 2.2: place(fx, groan(2.3, 60 + 8 * (k % 2), 0.06 + 0.012 * min(k, 5)), ts, pan=(-0.4 if k % 2 else 0.4))
    place(fx, groan(1.7, 66, 0.12), T["fall"] + 0.1); place(fx, riser(1.2, 0.07), T["brk"] - 1.2)
    place(fx, snap(0.55), T["brk"]); place(fx, snap(0.35), T["brk"] + 0.22); place(fx, boom(36, 3.0, 0.75), T["brk"] + 0.03); place(fx, crash(3.0, 0.34), T["brk"] + 0.05)
    place(fx, splash(2.6, 0.2), T["brk"] + 3.3)   # sqrt(60 / 4.9) = 3.5 s for the fall to the water
    place(fx, snap(0.4), T["gone"]); place(fx, crash(2.6, 0.3), T["gone"] + 0.05); place(fx, boom(40, 2.4, 0.55), T["gone"] + 0.4); place(fx, splash(2.4, 0.07), T["gone"] + 1.6)
    place(fx, boom(44, 2.0, 0.2), T["toll"] + 0.05); place(fx, bell(440, 2.2, 0.03), T["toll"] + 0.2)
    place(fx, bell(660, 2.0, 0.018), 51.6, pan=0.3); place(fx, riser(1.0, 0.035), 54.7)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/tacoma.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
