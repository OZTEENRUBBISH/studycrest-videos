"""Soundtrack + narration for the held-breath simulation. Writes work/breath.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 49.4
LINES = [(0.4, "What if you held your breath for as long as you could?"),
 (2.9, "You'd think you run out of oxygen. You don't. The urge to breathe comes mainly from carbon dioxide building up."),
 (9.5, "You're at the pool. Deep breath, and under. Cool water on your face slows your heart: the dive reflex."),
 (15.6, "Your cells keep making carbon dioxide. With nowhere to go, it builds in your blood."),
 (21.1, "Sensors in your brainstem notice. Most people give in after about a minute. Yet your lungs held enough oxygen for about four."),
 (29.1, "Then you break, and breathe."),
 (31.3, "The danger is cheating that urge. Breathing fast first flushes out carbon dioxide, so the warning comes late, and you can black out underwater."),
 (40.4, "Never hold your breath in water alone."),
 (43.0, "You're not out of oxygen. It's mostly carbon dioxide telling you to breathe."), (47.6, "Follow for more.")]
CHUNKS = [[], ["You'd think you<br><em>run out of oxygen</em>.", "You <em>don't</em>.", "The urge to breathe", "comes <em>mainly</em> from", "<em>carbon dioxide</em><br>building up."],
 ["You're at the pool.", "Deep breath,", "and under.", "Cool water on your face", "<em>slows your heart</em>:", "the <em>dive reflex</em>."],
 ["Your cells keep making<br><em>carbon dioxide</em>.", "With nowhere to go,", "it <em>builds</em><br>in your blood."],
 ["Sensors in your<br><em>brainstem</em> notice.", "Most people give in", "after about <em>a minute</em>.", "Yet your lungs held<br>enough oxygen", "for about <em>four</em>."],
 ["Then you break,", "and <em>breathe</em>."],
 ["The danger is<br><em>cheating that urge</em>.", "Breathing fast first", "flushes out<br><em>carbon dioxide</em>,", "so the warning<br>comes <em>late</em>,", "and you can <em>black out</em><br>underwater."],
 ["<em>Never</em> hold your breath<br>in water <em>alone</em>."],
 ["You're <em>not</em> out of oxygen.", "It's mostly <em>carbon dioxide</em>", "telling you to breathe."], []]
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
    def heart(lvl=0.16): d = 0.5; t = np.arange(int(d * SR)) / SR; x = np.sin(2 * np.pi * 52 * t) * np.exp(-t * 22); k = int(0.16 * SR); y = x.copy(); y[k:] += x[:-k] * 0.7; return lp(y, 160) * lvl
    def alarm(lvl=0.035, f=880): d = 0.22; t = np.arange(int(d * SR)) / SR; return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2 * t)) * np.sin(np.pi * t / d) ** 2 * lvl
    def gasp(lvl=0.07, d=0.8): m = int(d * SR); t = np.arange(m) / SR; return bp(noise(d), 700, 4200) * np.sin(np.pi * t / d) ** 1.5 * lvl
    def puff(lvl=0.04): return gasp(lvl, 0.22)
    def thud(lvl=0.2): d = 0.3; t = np.arange(int(d * SR)) / SR; return np.sin(2 * np.pi * 70 * t) * np.exp(-t * 18) * lvl
    def kids(d, lvl=0.012): t = np.arange(int(d * SR)) / SR; return bp(noise(d), 900, 3200) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.7 * t) ** 2) * (0.5 + 0.5 * np.sin(2 * np.pi * 2.3 * t + 1) ** 4) * env(d, 0.4, 0.5) * lvl
    bed = np.zeros((n, 2)); fx = np.zeros((n, 2)); vo = np.zeros(n)
    # beds: the pool, the flash-forward underwater, the pool again, under, the blood vessel, the alarm, the surface, the shortcut, the rule, the close
    place(bed, pad(["D2", "A2", "F3", "A3"], 3.2, 0.4, 0.5, 0.032), 0.0); place(bed, waves(3.0, 0.045), 0.0); place(bed, kids(2.9, 0.02), 0.0); place(bed, shimmer(2.8, 0.014), 0.1)
    place(bed, pad(["C2", "G2", "E3", "G3"], 6.9, 0.3, 0.5, 0.04), 2.8); place(bed, deep(6.6, 0.05, 260), 2.9)
    place(bed, pad(["F2", "C3", "A3", "E4"], 6.4, 0.5, 0.6, 0.032), 9.4); place(bed, waves(2.7, 0.045), 9.4); place(bed, kids(2.6, 0.02), 9.4); place(bed, deep(3.5, 0.04, 320), 12.1)
    place(bed, pad(["D2", "A2", "D3", "F3"], 5.8, 0.4, 0.6, 0.042), 15.5); place(bed, deep(5.5, 0.05, 150), 15.6)
    place(bed, pad(["A1", "E2", "C3", "G3"], 8.3, 0.5, 0.5, 0.044), 21.0); place(bed, deep(8.0, 0.05, 240), 21.1)
    place(bed, pad(["G2", "D3", "B3", "E4"], 2.6, 0.2, 0.5, 0.034), 29.0); place(bed, waves(2.3, 0.05), 29.2); place(bed, kids(2.0, 0.02), 29.3)
    place(bed, pad(["C2", "G2", "E3", "G3"], 9.4, 0.5, 0.6, 0.044), 31.2); place(bed, waves(4.0, 0.03), 31.3); place(bed, deep(5.0, 0.06, 200), 35.4)
    place(bed, pad(["E2", "B2", "G3", "D4"], 2.9, 0.3, 0.5, 0.036), 40.3); place(bed, waves(2.6, 0.04), 40.4)
    place(bed, pad(["D2", "A2", "D3", "F3", "A3", "E4"], 6.2, 0.4, 2.0, 0.038), 42.9); place(bed, waves(6.0, 0.05), 43.0); place(bed, kids(4.0, 0.016), 43.0); place(bed, shimmer(5.6, 0.016), 43.1)
    # effects
    place(fx, boom(70, 0.7, 0.2), 0.03); place(fx, splash(0.05), 1.2, pan=0.4); place(fx, whoosh(0.5, 0.07), 2.6)
    place(fx, boom(46, 1.0, 0.36), 2.9); place(fx, bubbles(1.4, 0.05, 8), 3.0); place(fx, riser(1.6, 0.045), 3.6); place(fx, boom(52, 0.8, 0.34), 5.2); place(fx, ding(0.05), 5.3)
    for k in range(4): place(fx, alarm(0.035), 7.6 + k * 0.36)
    for k, tt in enumerate([3.2, 4.0, 4.8, 6.0, 6.8, 8.9]): place(fx, heart(0.12), tt)
    place(fx, whoosh(0.5, 0.09), 9.35); place(fx, gasp(0.07, 1.0), 10.5); place(fx, splash(0.16), 11.95); place(fx, bubbles(1.8, 0.09, 16), 12.0)
    for tt in [12.7, 13.5, 14.4, 15.4]: place(fx, heart(0.2), tt)
    place(fx, whoosh(0.6, 0.09), 15.45); place(fx, boom(44, 1.0, 0.3), 15.6)
    for k, tt in enumerate(np.arange(16.0, 21.0, 1.0)): place(fx, heart(0.2), float(tt))
    for k in range(14): place(fx, ting(700 + 90 * k, 0.3, 0.012 + 0.0015 * k), 16.2 + k * 0.33, pan=(-1) ** k * 0.5)
    place(fx, riser(1.6, 0.04), 19.4)
    place(fx, whoosh(0.5, 0.08), 21.0); place(fx, ding(0.045), 21.9)
    for k in range(3): place(fx, alarm(0.03), 22.2 + k * 0.36)
    for tt in [24.3, 25.3, 26.4, 27.5, 28.5]: place(fx, heart(0.2), tt)
    place(fx, ding(0.04), 27.3); place(fx, riser(1.2, 0.05), 27.9)
    place(fx, whoosh(0.4, 0.09), 29.0); place(fx, splash(0.17), 29.25); place(fx, gasp(0.09, 0.9), 29.5); place(fx, gasp(0.06, 0.7), 30.5)
    place(fx, whoosh(0.5, 0.09), 31.15); place(fx, boom(46, 0.9, 0.3), 31.3)
    for k in range(9): place(fx, puff(0.045), 32.6 + k * 0.3)
    place(fx, splash(0.14), 35.3); place(fx, bubbles(1.2, 0.07, 12), 35.35)
    for tt in [36.0, 36.9, 37.9, 39.0]: place(fx, heart(0.2 - (tt - 36) * 0.03), tt)
    place(fx, riser(2.0, 0.035), 37.6); place(fx, boom(38, 2.0, 0.42), 39.3)
    place(fx, whoosh(0.5, 0.08), 40.25); place(fx, splash(0.08), 40.4); place(fx, ding(0.05), 40.6)
    place(fx, whoosh(0.6, 0.09), 42.9); place(fx, ding(0.05), 43.3); place(fx, splash(0.05), 44.6, pan=-0.4); place(fx, ding(0.045), 45.2); place(fx, riser(1.0, 0.035), 46.3)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/breath.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
