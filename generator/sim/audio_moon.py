"""Soundtrack + narration for the Moon-disappeared simulation. Writes work/moon.wav"""
import os, sys, wave, numpy as np
from scipy import signal
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DUR = 48.6
LINES = [(0.4, "What if the Moon disappeared, tonight?"),
 (3.0, "You're at a fishing harbour, under a full Moon. And it has just vanished. You'd expect the tides to stop. They won't."),
 (9.5, "First comes the dark. The Moon's last light reaches you one point three seconds later. Then there are only stars."),
 (16.4, "Earth doesn't fly away. It keeps circling the Sun, almost exactly as before."),
 (21.3, "And the sea still rises and falls. Because the Sun pulls on the oceans too, about forty six percent as hard as the Moon did."),
 (29.3, "So the tides shrink to less than half. And high tide now arrives at the same time every day, instead of about fifty minutes later."),
 (37.3, "Over millions of years, Earth's tilt could start to wander, and the seasons with it."),
 (41.8, "The Moon never made the tides alone. It only made most of them."),
 (46.1, "Follow for more.")]
CHUNKS = [[], ["You're at a fishing harbour,", "under a <em>full Moon</em>.", "And it has just <em>vanished</em>.", "You'd expect the tides to stop.", "They <em>won't</em>."],
 ["First comes the dark.", "The Moon's last light reaches you", "<em>1.3 seconds</em> later.", "Then there are only <em>stars</em>."],
 ["Earth doesn't fly away.", "It keeps circling the Sun,", "almost exactly as before."],
 ["And the sea still<br>rises and falls.", "Because the <em>Sun</em> pulls<br>on the oceans too,", "about <em>46 percent</em> as hard<br>as the Moon did."],
 ["So the tides shrink<br>to <em>less than half</em>.", "And high tide now arrives", "at the <em>same time</em> every day,", "instead of about<br>50 minutes later."],
 ["Over millions of years,", "Earth's tilt could<br>start to <em>wander</em>,", "and the seasons with it."],
 ["The Moon never made<br>the tides alone.", "It only made <em>most</em> of them."], []]
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
    # beds: harbour at night, the dark, the orbit diagram, the tide diagram, the sped-up harbour, the tilt, dawn
    place(bed, surf(16.6, 0.045), 0.0); place(bed, pad(["A2", "E3", "A3", "C4"], 9.8, 1.2, 0.8, 0.032), 0.0); place(bed, shimmer(6.0, 0.012), 0.2)
    for ts in [1.2, 5.1, 11.3]: place(bed, creak(0.6, 0.016), ts, pan=0.3)
    place(bed, bell(660, 2.4, 0.02), 2.2, pan=-0.4); place(bed, bell(660, 2.4, 0.016), 8.0, pan=-0.4)
    place(bed, pad(["D2", "A2", "F3"], 7.2, 0.6, 0.8, 0.04), 9.4); place(bed, rumble(3.0, 0.03) * env(3.0, 0.2, 1.2), 14.2)
    place(bed, pad(["E2", "B2", "E3", "G3"], 5.2, 0.5, 0.5, 0.036), 16.2); place(bed, shimmer(4.8, 0.013), 16.3)
    place(bed, pad(["C2", "G2", "E3", "B3"], 8.2, 0.5, 0.6, 0.038), 21.2); place(bed, shimmer(7.6, 0.012, ("E5", "G5", "B5", "D6")), 21.4)
    place(bed, surf(8.2, 0.055, 2.67), 29.2); place(bed, pad(["F2", "C3", "A3", "E4"], 8.2, 0.5, 0.6, 0.036), 29.2); place(bed, gulls(3.0, 0.014, 3), 31.4, pan=0.3)
    place(bed, pad(["B1", "F2", "B2", "D3"], 4.7, 0.5, 0.5, 0.042), 37.2); place(bed, shimmer(4.2, 0.012, ("D5", "F5", "A5", "C6")), 37.3)
    place(bed, surf(6.9, 0.05), 41.7); place(bed, gulls(5.5, 0.018, 8), 42.0, pan=-0.2); place(bed, pad(["A2", "E3", "A3", "C4", "E4", "B4"], 6.9, 0.5, 1.8, 0.034), 41.7)
    # effects
    place(fx, riser(1.2, 0.05), 5.0); place(fx, boom(54, 1.2, 0.3), 6.2); place(fx, tick(900, 0.08), 6.2)
    for k in range(8): place(fx, tick(1000, 0.045), 7.2 + k * 1.0)
    place(fx, riser(1.4, 0.07), 12.8); place(fx, boom(38, 2.8, 0.55), 14.2)
    for ts in [16.3, 21.2, 29.2, 37.2, 41.7]: place(fx, whoosh(0.55, 0.07), ts - 0.25)
    place(fx, boom(52, 1.0, 0.2), 16.3); place(fx, boom(56, 0.9, 0.2), 26.0); place(fx, whoosh(1.0, 0.05), 25.6)
    place(fx, boom(48, 1.0, 0.2), 37.2); place(fx, riser(1.2, 0.05), 40.6)
    rep = []
    for k, (ts, txt) in enumerate(LINES):
        v = speak(txt); i = int(ts * SR); v = v[: n - i]; vo[i:i + len(v)] += v * 0.62; nxt = LINES[k + 1][0] if k + 1 < len(LINES) else DUR
        rep.append((ts, round(len(v) / SR, 2), "OVERLAP" if ts + len(v) / SR - 0.1 > nxt else "ok"))
    e = np.sqrt(lp(vo ** 2, 6, 1).clip(0)); duck = 1 - 0.55 * np.clip(e / 0.1, 0, 1)
    fade = np.ones(n); fade[-int(0.7 * SR):] = np.linspace(1, 0, int(0.7 * SR))
    m = np.tanh(((bed + fx * 0.9) * duck[:, None] + vo[:, None]) * fade[:, None] * 1.1); m = m / np.max(np.abs(m)) * 0.85
    with wave.open(BASE + "/work/moon.wav", "wb") as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((m * 32767).astype(np.int16).tobytes())
    print([r for r in rep if r[2] != "ok"] or "all lines fit", rep)
