"""Caption timings from the narration. caps.py <name>: reads LINES and CHUNKS from audio_<name>.py (import-safe: guarded by __main__),
splits each line's spoken time between its caption chunks in proportion to how long each chunk takes to say,
and writes the result into <name>.html between /*CAPS*/ and /*END*/."""
import sys, os, re, json, importlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from vo import speak, SR, BASE
name = sys.argv[1]; m = importlib.import_module("audio_" + name); out = []
for (ts, txt), chunks in zip(m.LINES, m.CHUNKS):
    if not chunks: continue
    tot = len(speak(txt)) / SR - 0.05; plain = [re.sub(r"<[^>]+>", " ", c).replace("  ", " ").strip() for c in chunks]
    d = [len(speak(p + ("" if p[-1] in ".?!:," else "."))) / SR - 0.05 for p in plain]; k = tot / sum(d); t = ts
    for c, dd in zip(chunks, d): out.append([round(t, 2), round(t + dd * k - 0.02, 2), c]); t += dd * k
p = f"{BASE}/{name}.html"; s = open(p, encoding="utf-8").read()
s2 = re.sub(r"/\*CAPS\*/.*?/\*END\*/", lambda _: "/*CAPS*/" + json.dumps(out, ensure_ascii=False) + "/*END*/", s, flags=re.S); assert s2 != s or "/*CAPS*/" in s
open(p, "w", encoding="utf-8").write(s2); print("captions", len(out))
