#!/bin/bash
# Installs what the reel-editor skill needs (Python packages, ffmpeg, Arabic fonts) in Claude Code cloud sessions.
set -euo pipefail
[ "${CLAUDE_CODE_REMOTE:-}" = "true" ] || exit 0

# av is pinned: faster-whisper 1.2 passes metadata_errors= to av.open(), which PyAV 19 no longer accepts
pip install -q --root-user-action=ignore pillow numpy arabic-reshaper python-bidi faster-whisper onnxruntime fonttools "av>=14,<16"

if command -v apt-get >/dev/null; then
  pkgs="fonts-noto-core fonts-lemonada fonts-hosny-amiri"
  command -v ffmpeg >/dev/null || pkgs="$pkgs ffmpeg"
  apt-get install -y -qq $pkgs >/dev/null 2>&1 || { apt-get update -qq >/dev/null 2>&1 && apt-get install -y -qq $pkgs >/dev/null 2>&1; } || true
fi
