#!/usr/bin/env python3
"""
TTS wrapper for Zaphod's Head.

Uses Piper TTS (local, offline) to speak text through the system speaker.
Falls back to macOS `say` on development machines.
Returns False silently if neither is available — the rest of the system keeps working.

Setup: run ./setup_piper.sh on the Pi before using this.
"""

import os
import subprocess
import sys
import tempfile

# ---------------------------------------------------------------------------
# Config — adjust paths if you install Piper elsewhere
# ---------------------------------------------------------------------------
PIPER_BINARY = os.path.expanduser("~/piper/piper")
PIPER_MODEL  = os.path.expanduser("~/piper-models/en_US-lessac-medium.onnx")


# ---------------------------------------------------------------------------
# Internal playback helpers
# ---------------------------------------------------------------------------

def _play_wav(wav_path: str):
    """Play a WAV file. afplay on macOS, aplay on Linux/Pi."""
    if sys.platform == "darwin":
        subprocess.run(["afplay", wav_path], check=True, capture_output=True)
    else:
        subprocess.run(["aplay", "-q", wav_path], check=True, capture_output=True)


def _speak_piper(text: str) -> bool:
    """Speak via Piper TTS binary. Returns True on success."""
    if not os.path.exists(PIPER_BINARY) or not os.path.exists(PIPER_MODEL):
        return False

    wav_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            wav_path = f.name

        proc = subprocess.run(
            [PIPER_BINARY, "--model", PIPER_MODEL, "--output_file", wav_path],
            input=text.encode(),
            capture_output=True,
            timeout=15,
        )

        if proc.returncode == 0 and os.path.getsize(wav_path) > 0:
            _play_wav(wav_path)
            return True

    except Exception:
        pass

    finally:
        if wav_path and os.path.exists(wav_path):
            try:
                os.unlink(wav_path)
            except Exception:
                pass

    return False


def _speak_macos(text: str) -> bool:
    """Speak via macOS built-in `say`. Dev fallback only."""
    if sys.platform != "darwin":
        return False
    try:
        # Samantha is the closest built-in voice to a smug British affect
        subprocess.run(["say", "-v", "Samantha", text], check=True, capture_output=True, timeout=30)
        return True
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def speak(text: str) -> bool:
    """
    Speak text aloud. Tries Piper first, then macOS `say`, then gives up quietly.
    Returns True if audio actually played.
    """
    if _speak_piper(text):
        return True
    if _speak_macos(text):
        return True
    return False


def is_available() -> bool:
    """True if any TTS backend is usable right now."""
    if os.path.exists(PIPER_BINARY) and os.path.exists(PIPER_MODEL):
        return True
    if sys.platform == "darwin":
        return True
    return False


def status() -> str:
    """Human-readable status of TTS backends."""
    if os.path.exists(PIPER_BINARY) and os.path.exists(PIPER_MODEL):
        return "piper (offline)"
    if sys.platform == "darwin":
        return "macOS say (dev fallback)"
    return "unavailable — run setup_piper.sh"


if __name__ == "__main__":
    # Quick test
    import sys
    text = " ".join(sys.argv[1:]) or "I have a brain the size of a planet and they ask me to test text to speech."
    print(f"TTS status: {status()}")
    print(f"Speaking: {text}")
    ok = speak(text)
    if not ok:
        print("No TTS backend available. Run setup_piper.sh on the Pi.")
