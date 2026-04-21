#!/bin/bash
# Setup Piper TTS for Zaphod's Head
# Run this once on the Raspberry Pi before using tts.py
#
# Piper releases: https://github.com/rhasspy/piper/releases
# Voice models:   https://huggingface.co/rhasspy/piper-voices
#
# This script downloads:
#   - Piper binary  → ~/piper/piper
#   - Voice model   → ~/piper-models/en_US-lessac-medium.onnx

set -e

PIPER_DIR="$HOME/piper"
MODELS_DIR="$HOME/piper-models"
MODEL_NAME="en_US-lessac-medium"

mkdir -p "$PIPER_DIR" "$MODELS_DIR"

# ---------------------------------------------------------------------------
# Detect architecture
# ---------------------------------------------------------------------------
ARCH=$(uname -m)
case "$ARCH" in
  aarch64) PIPER_ARCH="aarch64" ;;
  armv7l)  PIPER_ARCH="armv7l"  ;;
  x86_64)  PIPER_ARCH="x86_64"  ;;
  *)
    echo "Unknown architecture: $ARCH"
    echo "Download the Piper binary manually from https://github.com/rhasspy/piper/releases"
    exit 1
    ;;
esac

# ---------------------------------------------------------------------------
# Download Piper binary
# ---------------------------------------------------------------------------
if [ -f "$PIPER_DIR/piper" ]; then
  echo "Piper binary already exists at $PIPER_DIR/piper — skipping download."
else
  echo "Fetching latest Piper release for $PIPER_ARCH..."
  LATEST=$(curl -s https://api.github.com/repos/rhasspy/piper/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
  if [ -z "$LATEST" ]; then
    echo "Could not fetch latest release tag. Check your internet connection."
    echo "Download manually from: https://github.com/rhasspy/piper/releases"
    exit 1
  fi
  echo "Latest release: $LATEST"
  TARBALL="piper_linux_${PIPER_ARCH}.tar.gz"
  URL="https://github.com/rhasspy/piper/releases/download/${LATEST}/${TARBALL}"
  echo "Downloading $URL..."
  curl -L "$URL" | tar -xz -C "$PIPER_DIR" --strip-components=1
  echo "Piper installed at $PIPER_DIR/piper"
fi

# ---------------------------------------------------------------------------
# Download voice model
# ---------------------------------------------------------------------------
ONNX_FILE="$MODELS_DIR/${MODEL_NAME}.onnx"
JSON_FILE="$MODELS_DIR/${MODEL_NAME}.onnx.json"

if [ -f "$ONNX_FILE" ] && [ -f "$JSON_FILE" ]; then
  echo "Model $MODEL_NAME already exists — skipping download."
else
  echo "Downloading voice model: $MODEL_NAME..."
  MODEL_BASE="https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium"
  curl -L --progress-bar "${MODEL_BASE}/${MODEL_NAME}.onnx"      -o "$ONNX_FILE"
  curl -L --progress-bar "${MODEL_BASE}/${MODEL_NAME}.onnx.json" -o "$JSON_FILE"
  echo "Model saved to $MODELS_DIR/"
fi

# ---------------------------------------------------------------------------
# Smoke test
# ---------------------------------------------------------------------------
echo ""
echo "Testing Piper..."
echo "Two heads, three arms, zero interest in your problems." \
  | "$PIPER_DIR/piper" --model "$ONNX_FILE" --output_raw \
  | aplay -r 22050 -f S16_LE -t raw -q - 2>/dev/null \
  && echo "Audio OK." \
  || echo "aplay not found or audio device missing — install with: sudo apt install alsa-utils"

echo ""
echo "Setup complete."
echo "  Binary: $PIPER_DIR/piper"
echo "  Model:  $ONNX_FILE"
echo ""
echo "Test with: python tts.py"
