#!/bin/sh
# One-time setup in a fresh workspace: Python packages and the Kokoro voice model (Apache-2.0).
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile scipy numpy pillow
mkdir -p kokoro wav timings silent out
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "kokoro/$f" ] || curl -sS -L -o "kokoro/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
echo "setup done"
