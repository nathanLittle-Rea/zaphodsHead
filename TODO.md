# Zaphod's Head — Project TODO

Halloween animatronic second head for a Zaphod Beeblebrox costume.
Head 2 listens to ambient conversation, responds in Zaphod's voice,
and feeds one-liners to Head 1 (you) via earpiece.

---

## CONNECTIVITY OPTIONS (pick one)

| Option | Setup | Quality | Cost |
|---|---|---|---|
| **A) Ollama on Pi (recommended)** | Install Ollama + model on Pi 5 8GB | Good for one-liners | Free, fully offline |
| **B) Phone hotspot → Cloud API** | Pi connects to phone WiFi, calls Claude | Best quality | ~$0.01/call, needs signal |
| **C) Phone as compute bridge** | Pi sends text to phone via BT/WiFi, phone runs Ollama (Android+Termux) or Cloud | Varies | Complex setup |

**Recommended model for Option A:** `llama3.2:3b` (fast on Pi 5) or `phi3:mini`
**Install:** `curl -fsSL https://ollama.ai/install.sh | sh && ollama pull llama3.2:3b`

---

## PHASE 1 — Response Engine
- [x] `zaphod_bot.py` — Cloud version (Claude API, needs internet)
- [x] `zaphod_local.py` — Local version (Ollama, fully offline)
  - Calls Ollama API with few-shot system prompt
  - 8-second timeout then falls back to pre-baked line bank
  - Pre-baked bank of 20 canonical Zaphod lines (zero latency)
- [ ] Tune few-shot examples in system prompt based on testing
- [ ] Grow the pre-baked line bank to 50–100 lines
- [ ] Run `python zaphod_local.py --test` to verify model is working

---

## PHASE 2 — Voice I/O

### Text-to-Speech (Head 2's speaker)
- [ ] Integrate TTS API (ElevenLabs / OpenAI TTS / Google Cloud TTS)
  - Needs a slightly nasal, cocky British-ish accent
  - ElevenLabs "voice cloning" or custom voice probably best for character accuracy
- [ ] Output audio to speaker wired into Head 2
- [ ] Tune volume, EQ for hollow animatronic head acoustics
- [ ] Separate audio output channel for earpiece (Head 1 only)

### Speech-to-Text (ambient listening)
- [ ] Integrate STT (Whisper / Google Speech / Deepgram)
- [ ] Continuous ambient listening with VAD (Voice Activity Detection)
  - Don't transcribe every sound — only when someone is clearly speaking
- [ ] Keyword / wake-word detection for Head 1 → Head 2 direct prompts
  - e.g., "Hey Zaphod…" triggers a directed response rather than ambient reaction

---

## PHASE 3 — Trigger Logic & Response Modes

Three distinct modes:

### Mode A — Ambient Reaction (passive)
- [ ] Listen to conversation snippets
- [ ] Randomly decide whether to react (e.g., 20–40% chance per conversational exchange)
- [ ] Send snippet as context to Claude → Zaphod response → TTS → Head 2 speaker
- [ ] Minimum cooldown between responses (e.g., 30–60 seconds) so it's not overwhelming

### Mode B — Direct Prompt (Head 1 → Head 2)
- [ ] Head 1 speaks a trigger phrase followed by a prompt
- [ ] Head 2 generates and speaks a full response via its speaker
- [ ] Example: "Zaphod, what do you think about this party?"

### Mode C — Earpiece One-Liner (Head 1 private)
- [ ] Head 1 speaks a separate trigger phrase (or button press)
- [ ] One-liner generated and played ONLY to earpiece, not Head 2 speaker
- [ ] Head 1 can then choose to say it out loud as if it's their own wit
- [ ] Low latency critical here — target < 3 seconds end-to-end

---

## PHASE 4 — Hardware

### Head 2 Physical Build
- [ ] Sculpt / source a second head (foam, latex, resin, or found prop)
- [ ] Mount speaker internally
- [ ] Mount Raspberry Pi (or similar) inside or in costume body
- [ ] Animatronic jaw sync to audio output (optional but amazing)
  - Servo driver board + small servo for jaw movement
  - Jaw movement triggered by audio amplitude
- [ ] LED eyes (optional — blue or glowing for sci-fi vibe)
- [ ] Weatherproofing for outdoor use (Halloween)

### Electronics
- [ ] Raspberry Pi 5 (or Pi 4) as main compute
- [ ] USB microphone array (or lapel mic for ambient pickup)
- [ ] Bluetooth earpiece for Head 1
- [ ] Small amplified speaker for Head 2
- [ ] Battery pack (USB-C PD, run all day on party battery)
- [ ] Optional: physical button/toggle for mode switching

### Connectivity
- [ ] Decide: on-device inference vs cloud API
  - Cloud API (Anthropic + ElevenLabs): better quality, needs phone hotspot
  - On-device (Whisper + small LLM): worse quality, fully offline
  - Recommended: Cloud for response quality, Whisper locally for STT latency

---

## PHASE 5 — Software Architecture

- [ ] Main orchestration loop (Python asyncio)
  - Mic input → STT → trigger detection → Claude → TTS → audio output
  - Handle Mode A / B / C switching
- [ ] Config file for:
  - Response probability (ambient mode)
  - Cooldown timers
  - Trigger phrases
  - API keys
  - Audio device IDs
- [ ] Logging / debug mode (text output of all responses for testing without hardware)
- [ ] Graceful fallback if API call fails (pre-cached responses)

---

## PHASE 6 — Testing & Polish

- [ ] Test in realistic party noise conditions
- [ ] Tune ambient listening sensitivity (avoid false triggers)
- [ ] Curate a bank of 20–30 pre-generated Zaphod responses for zero-latency injection
- [ ] Dry run the full costume at least one week before Halloween
- [ ] Test battery life under continuous use

---

## STRETCH GOALS
- [ ] Jaw animatronics synced to speech
- [ ] Zaphod recognizes specific people (face detection → personalised insults)
- [ ] "Drunk mode" — gradually more unhinged responses as the night goes on
- [ ] Marvin the Paranoid Android as a foil (separate audio track for contrast)
- [ ] Post-Halloween: turn this into a standalone prop / convention piece

---

## KEY DEPENDENCIES

| Component | Candidate | Notes |
|---|---|---|
| LLM (offline) | Ollama + llama3.2:3b | Free, runs on Pi 5 8GB, ~2-4s latency |
| LLM (cloud fallback) | Anthropic Claude API | Best quality, needs hotspot |
| TTS | Piper TTS (offline) or ElevenLabs (cloud) | Piper runs on Pi, ElevenLabs is higher quality |
| STT | OpenAI Whisper (local, tiny/base model) | Runs on Pi, ~1s latency |
| Compute | Raspberry Pi 5 — **8GB RAM required** | 4GB can run model but will be slow |
| Audio out | USB audio + mini amp + 3W speaker | ~$15 total |
| Earpiece | Bluetooth (BLE) | Jaybird / Jabra recommended |
