# Zaphod's Head

An animatronic second head for a Zaphod Beeblebrox Halloween costume. The head runs on a Raspberry Pi 5, generates one-liners in Zaphod's voice using a local LLM, and speaks them through a built-in speaker. Head 1 (you) can also receive private lines via earpiece so you can deliver them as your own wit.

Fully offline. No WiFi required at the party.

---

## How it works

A small LLM (`llama3.2:3b`) runs on the Pi via [Ollama](https://ollama.ai). It's guided by an extensive system prompt that nails Zaphod's voice — narcissistic, breezy, two-headed, never rattled. A growing bank of curated examples (`examples.json`) is injected into every request, compounding quality over time. If the model is too slow or unavailable, it falls back to a pre-baked bank of 20 canonical lines instantly.

---

## Files

| File | Purpose |
|---|---|
| `zaphod_local.py` | Main bot — Ollama API, fallback line bank, CLI |
| `curator.py` | Interactive curation tool — generate, refine, and save examples |
| `zaphod_bot.py` | Cloud version using the Anthropic API (optional) |
| `examples.json` | Curated one-liners injected into the system prompt at runtime |
| `TODO.md` | Full project roadmap (hardware, voice I/O, modes) |

---

## Requirements

- Python 3.10+ (stdlib only for `zaphod_local.py` and `curator.py`)
- [Ollama](https://ollama.ai) running locally with `llama3.2:3b` pulled
- Raspberry Pi 5 **8GB** recommended (4GB will be slow)

```bash
# Install Ollama and pull the model (on the Pi)
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull llama3.2:3b
```

For the cloud version only:
```bash
pip install anthropic
export ANTHROPIC_API_KEY=your_key_here
```

---

## Usage

### Run the bot

```bash
# Single line from a prompt
python zaphod_local.py "someone just complimented my costume"

# Interactive REPL
python zaphod_local.py -i

# Pre-load the model into RAM before the party (recommended)
python zaphod_local.py --warmup
```

### Curate examples

The curator grows `examples.json`, which is injected into every future request as style reference. More good examples = better outputs.

```bash
python curator.py
```

**Curator flow:**
1. Enter a situation prompt
2. Get 5 Zaphod one-liners, each with a different approach (charming, dismissive, witty, outrageous, self-aggrandising)
3. At the `>` prompt:
   - Type numbers to save lines: `1 3` saves lines 1 and 3
   - Type a refinement note to regenerate all 5: `more tongue in cheek`
   - `r` to regenerate as-is
   - `q` to enter a new prompt

### Cloud version (optional)

Requires an `ANTHROPIC_API_KEY` and internet access (phone hotspot works).

```bash
python zaphod_bot.py "what do you think about the meaning of life?"
python zaphod_bot.py --one-liner "someone just doubted you"
```

---

## Prompt engineering notes

All lines must be **first person, spoken directly to another person** — never narration or third-person commentary. This is enforced in the system prompt and few-shot examples. If you save a line that talks *about* a person rather than *to* them, it will corrupt future outputs — delete it from `examples.json` manually.

---

## Roadmap

See [`TODO.md`](TODO.md) for the full phased plan:

- **Phase 2** — Voice I/O: TTS (Piper offline / ElevenLabs cloud) + STT (Whisper)
- **Phase 3** — Trigger modes: ambient reaction, direct prompt, private earpiece
- **Phase 4** — Hardware: animatronic jaw, LED eyes, battery pack
- **Phase 5** — Asyncio orchestration loop with config file
- **Phase 6** — Party testing and polish

---

## Zaphod's voice — quick reference

| Slang | Meaning |
|---|---|
| froody | really cool/together |
| hoopy | really hip |
| zarking | expletive (like "bloody") |
| Belgium | the rudest word in the universe — use sparingly |

Key character beats: staggeringly narcissistic, effortlessly cool, casually wrong with total confidence, occasionally interrupted by [Head 2] with a contradictory take.
