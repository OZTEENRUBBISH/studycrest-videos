"""Film a simulation page frame by frame.
  render.py stills <page> t1 t2 ...        -> work/<page>-stills.jpg (contact sheet) + work/<page>-<t>.jpg
  render.py video <page> [t0 t1]           -> work/<page>-silent.mp4 (30 fps, 1080x1920)"""
import sys, os, time, subprocess, threading, http.server, functools, io
from playwright.sync_api import sync_playwright
BASE = os.path.dirname(os.path.abspath(__file__)); FPS = 30
def serve():
    h = functools.partial(http.server.SimpleHTTPRequestHandler, directory=BASE); h.log_message = lambda *a, **k: None
    s = http.server.ThreadingHTTPServer(("127.0.0.1", 0), h); threading.Thread(target=s.serve_forever, daemon=True).start(); return s.server_address[1]
def open_page(p, page):
    port = serve(); b = p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist", "--disable-gpu-vsync", "--hide-scrollbars"])
    pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1); errs = []
    pg.on("console", lambda m: errs.append(m.text) if m.type in ("error", "warning") else None); pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto(f"http://127.0.0.1:{port}/{page}.html" + os.environ.get("SIMQ", "")); 
    try: pg.wait_for_function("window.READY === true", timeout=120000)
    except Exception as e: print("NOT READY", errs[:8]); raise
    if errs: print("console:", errs[:6])
    return b, pg
def shot(pg, t):
    pg.evaluate("t => window.renderAt(t)", t); return pg.screenshot(type="jpeg", quality=93, clip={"x": 0, "y": 0, "width": 1080, "height": 1920})
if __name__ == "__main__":
    mode, page = sys.argv[1], sys.argv[2]; os.makedirs(BASE + "/work", exist_ok=True)
    with sync_playwright() as p:
        b, pg = open_page(p, page)
        if mode == "stills":
            from PIL import Image
            ts = [float(x) for x in sys.argv[3:]]; ims = []; t0 = time.time()
            for t in ts:
                d = shot(pg, t); open(f"{BASE}/work/{page}-{t:06.2f}.jpg", "wb").write(d); ims.append(Image.open(io.BytesIO(d)).resize((405, 720)))
            cols = min(len(ims), 6); rows = (len(ims) + cols - 1) // cols; sh = Image.new("RGB", (cols * 405, rows * 720))
            for i, im in enumerate(ims): sh.paste(im, ((i % cols) * 405, (i // cols) * 720))
            sh.save(f"{BASE}/work/{page}-stills.jpg", quality=85); print("stills", len(ts), "sec/frame", round((time.time() - t0) / len(ts), 2))
        else:
            dur = pg.evaluate("window.DUR"); t0 = float(sys.argv[3]) if len(sys.argv) > 3 else 0.0; t1 = float(sys.argv[4]) if len(sys.argv) > 4 else dur
            out = f"{BASE}/work/{page}-silent" + (f"-{t0:.1f}" if len(sys.argv) > 3 else "") + ".mp4"; tmp = out + ".tmp.mp4"
            ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg", "-i", "-", "-c:v", "libx264", "-crf", "17", "-preset", "medium", "-pix_fmt", "yuv420p", "-movflags", "+faststart", tmp], stdin=subprocess.PIPE)
            n0, n1 = round(t0 * FPS), round(t1 * FPS); st = time.time()
            for f in range(n0, n1):
                ff.stdin.write(shot(pg, f / FPS))
                if (f - n0) % 60 == 0: print(f"frame {f}/{n1}  {round((time.time() - st) / (f - n0 + 1), 2)} s/frame", flush=True)
            ff.stdin.close(); rc = ff.wait()
            if rc == 0: os.replace(tmp, out)
            print("done", out, "rc", rc, round(time.time() - st), "s")
        b.close()
