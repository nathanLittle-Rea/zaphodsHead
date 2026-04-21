# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Halloween costume prop: animatronic second head for a Zaphod Beeblebrox (Hitchhiker's Guide) costume. The head runs on a Raspberry Pi 5 (8GB), generates one-liners in Zaphod's voice via a local LLM, and speaks them through a built-in speaker. Head 1 (the user) can also receive private lines via earpiece.

**Primary constraint: must run fully offline at a party.** Ollama + `llama3.2:3b` on the Pi is the target. Cloud API (`zaphod_bot.py`) is an optional fallback via phone hotspot.

## Running the code

```bash
# Run the interactive bot (local Ollama, speaks if TTS available)
python zaphod_local.py -i

# Generate a single line from a prompt
python zaphod_local.py "someone just complimented my costume"

# Generate and speak aloud
python zaphod_local.py --speak "someone just complimented my costume"

# Pre-load the model into RAM before the party
python zaphod_local.py --warmup

# Test TTS (uses macOS `say` on dev machines, Piper on Pi)
python tts.py "Two heads, three arms, zero problems."

# Curate new examples into examples.json
python curator.py

# Cloud version (requires ANTHROPIC_API_KEY)
python zaphod_bot.py "what do you think about the meaning of life?"
python zaphod_bot.py --one-liner "someone doubted you"
```

No dependencies beyond Python stdlib for `zaphod_local.py`, `tts.py`, and `curator.py`. `zaphod_bot.py` requires `pip install anthropic`.

Ollama must be running locally: `ollama serve` with `llama3.2:3b` pulled.

Piper TTS: run `./setup_piper.sh` once on the Pi. On macOS, `tts.py` falls back to the built-in `say` command automatically.

## Architecture

```
zaphod_local.py   — primary bot, offline-first
tts.py            — TTS wrapper (Piper → aplay/afplay; macOS `say` as dev fallback)
curator.py        — curation UI for growing examples.json
zaphod_bot.py     — cloud fallback (Claude API via anthropic SDK)
examples.json     — curated one-liners, auto-injected into system prompt at runtime
setup_piper.sh    — one-shot Piper TTS installer for the Pi
```

**`zaphod_local.py`** is the core. It:
1. Builds a system prompt (`SYSTEM_PROMPT`) with Zaphod's voice, slang, and categorised few-shot examples
2. At call time, appends the most recent 20 entries from `examples.json` via `load_curated_examples()`
3. Posts to Ollama's HTTP API at `localhost:11434/api/generate`
4. Falls back to `LINE_BANK` (20 pre-baked lines) on timeout or failure

**`curator.py`** runs an interactive loop on a development machine to build `examples.json`:
- Enter a situation prompt → model generates 5 numbered variations
- Type numbers (e.g. `1 3`) to save those lines
- Type a note (e.g. `more tongue in cheek`) to regenerate all 5 with that note applied
- `r` to regenerate as-is, `q` for a new prompt

`examples.json` is the compounding asset — more curated examples = better outputs from the small model. Lines are injected as style reference, so quality of saved examples matters.

## Key model settings

| Setting | Value | Reason |
|---|---|---|
| `MODEL` | `llama3.2:3b` | Fits Pi 5 8GB, ~2-4s warm latency |
| `TIMEOUT_SEC` | 20 | Cold start on Pi 5 takes 15-20s |
| `MAX_TOKENS` | 60 | One-liners only |
| curator temperature | 0.95 | Max diversity across 5 variations |
| bot temperature | 0.85 | Consistent but not repetitive |

## Critical prompt constraints

All generated lines must be **first person, spoken directly TO another person** — never narration or third-person commentary. This is enforced in three places: the system prompt's `IMPORTANT` note, the user prompt template, and the few-shot examples which all use "you". Saved examples that violate this will pollute future outputs — check before saving.

## Planned phases

Voice I/O (TTS via Piper offline or ElevenLabs cloud, STT via Whisper), three response modes (ambient reaction, direct prompt, private earpiece), hardware assembly, and asyncio orchestration loop. See `TODO.md` for full roadmap.
