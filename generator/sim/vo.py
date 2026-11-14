"""Voice lines for the simulation videos (Kokoro, Apache-2.0). speak(text) -> mono float array at 48 kHz, cached."""
import os, hashlib, numpy as np
from scipy import signal
BASE = os.path.dirname(os.path.abspath(__file__)); GEN = os.path.dirname(BASE); SR = 48000
_k = None
def speak(text, voice="am_puck", speed=1.0):
    global _k
    h = hashlib.md5(f"{text}|{voice}|{speed}".encode()).hexdigest()[:16]; p = f"{BASE}/work/vo-{h}.npy"
    if os.path.exists(p): return np.load(p)
    from kokoro_onnx import Kokoro
    if _k is None: _k = Kokoro(GEN + "/kokoro/kokoro-v1.0.onnx", GEN + "/kokoro/voices-v1.0.bin")
    a, sr = _k.create(text.replace("StudyCrest", "Study Crest"), voice=voice, speed=speed, lang="en-us"); a = a.astype(np.float64)
    a = signal.resample_poly(a, SR, sr); idx = np.where(np.abs(a) > 0.01)[0]; a = a[max(0, idx[0] - 200): idx[-1] + 2400]
    a = signal.sosfilt(signal.butter(2, 85, "highpass", fs=SR, output="sos"), a)
    a = a + 0.3 * signal.sosfilt(signal.butter(1, 3500, "highpass", fs=SR, output="sos"), a)
    a = a / np.max(np.abs(a)); a = np.sign(a) * np.abs(a) ** 0.85; a = a / np.max(np.abs(a))
    np.save(p, a); return a
