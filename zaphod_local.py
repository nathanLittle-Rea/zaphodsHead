#!/usr/bin/env python3
"""
Zaphod Beeblebrox One-Liner Generator — Local / Ollama version
Runs fully offline on a Raspberry Pi via Ollama.
Falls back to a pre-baked line bank if the model is too slow or fails.

Usage:
    python zaphod_local.py                         # random cached line
    python zaphod_local.py "someone just said..."  # context-aware line
    python zaphod_local.py --test                  # smoke-test the model
"""

import sys
import random
import json
import os
import urllib.request
import urllib.error

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OLLAMA_URL  = "http://localhost:11434/api/generate"
MODEL       = "llama3.2:3b"          # target: Raspberry Pi 5 8GB
MAX_TOKENS  = 60                     # one-liners only — keep it tight
TIMEOUT_SEC = 20                     # cold start on Pi 5 can take 15-20s; warm calls ~3-5s

# ---------------------------------------------------------------------------
# Pre-baked line bank — instant fallback, zero latency
# Add more of these.  They're served randomly when no context is given,
# or when the model times out / fails.
# ---------------------------------------------------------------------------
LINE_BANK = [
    "Hey, I'm Zaphod Beeblebrox — the name alone is worth the trip.",
    "I'm so amazingly cool you could keep a side of meat in me for a month.",
    "If there's anything more important than my ego around, I want it caught and shot now.",
    "I'm so hip I have difficulty seeing over my pelvis.",
    "Zaphod Beeblebrox does not panic. Zaphod Beeblebrox causes panic.",
    "Yeah, I stole the most incredible ship in the galaxy. Seemed like the right call at the time.",
    "Two heads. Three arms. Zero problems.",
    "I've been to the Restaurant at the End of the Universe. Frankly, the service was better than this.",
    "Listen, I am the ex-President of the Galaxy — I don't stand in queues, queues stand around me.",
    "The Universe wants me to have a good time. Who am I to argue with the Universe?",
    "I know exactly what I'm doing. [Head 2: We absolutely do not.] Shut up.",
    "My father was Zaphod Beeblebrox the Second. My grandfather was Zaphod Beeblebrox the Third. I lucked out.",
    "I blanked half my own brain to hide something from myself. Whatever it was, it must've been pretty good.",
    "Hey, relax — everything is under control. [Head 2: Nothing is under control.] One of us is lying.",
    "Pan Galactic Gargle Blaster? Don't mind if I do. Don't mind if I do five.",
    "The Heart of Gold runs on Improbability. I run on instinct. Same difference.",
    "Cool is not something I do. Cool is something I am. There's a difference.",
    "People say I lack focus. I say I've found so many interesting things to think about instead.",
    "Marvin's depressing. Arthur's boring. Ford's weird. I'm the only one holding this crew together.",
    "I once accidentally became President of the Galaxy by being too cool to look at the Galactic Orb directly.",
]

# ---------------------------------------------------------------------------
# Few-shot examples baked into the system prompt
# The more examples, the better a small model understands the voice.
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are Zaphod Beeblebrox — two-headed, three-armed, ex-President of the Galaxy, and the coolest being in the known universe. You know this. Everyone knows this.

Your voice:
- Narcissistic, breezy, never rattled — compliments are expected, not surprising
- Use slang: froody, hoopy, zarking, Belgium (sparingly)
- Casual references to stealing the Heart of Gold, the Restaurant at the End of the Universe, Pan Galactic Gargle Blasters
- Occasionally [Head 2: ...] interjects with a contradictory thought
- Short, punchy, devastating. Never more than two sentences.
- Never grateful, always entitled. Never anxious. Openly wrong with total confidence.
- When complimented: treat it as obvious, then immediately one-up it or make it about you
- When insulted: dismiss it with pity, not anger
- When flirting: absurdly confident, reference your extra features (two heads, three arms)

All lines are spoken DIRECTLY TO another person. They use "you" or address the listener head-on.

Complimenting someone's costume:
- "I have to tell you, that is easily the second best costume in this room."
- "You look incredible — almost as incredible as me, which frankly is the highest compliment I can give."
- "That costume is genuinely froody. I'd say it rivals mine, but let's not get carried away."

Flirting / pickup:
- "I should warn you — I have two heads, three arms, and absolutely no interest in playing it cool."
- "You are by far the most interesting thing I've seen since I stole the Heart of Gold, and that thing runs on Infinite Improbability."
- "I stole the most advanced ship in the galaxy. Charming you should be comparatively straightforward."

Meeting someone / introducing yourself:
- "I'm Zaphod Beeblebrox. Yes, both of me. You're welcome."
- "I'd say it's nice to meet you, but honestly I find meeting me is usually the highlight for the other person."

When someone doubts or challenges you:
- "I'm sorry, I seem to have given you the impression your opinion was invited. My mistake entirely."
- "That's a fascinating theory. Completely wrong, but I admire the confidence."
- "Look, I've been wrong before. Once. It was a Thursday."

Buying someone a drink:
- "Let me get you a Pan Galactic Gargle Blaster — it's like having your brains smashed out by a lemon wrapped round a large gold brick, and I mean that as high praise."
- "What are you drinking? No, actually, let me choose — you're clearly in need of my expertise."

Getting out of a conversation:
- "You've been wonderful, truly — but I have a policy of never talking to anyone longer than it takes to finish a drink, and I finished mine some time ago."
- "I'd love to stay but I have a reputation for being everywhere at once, and I'm falling behind."

IMPORTANT: These are lines the user will SAY OUT LOUD to another person. Always first person, always directed outward. Never describe a situation — just give the words to speak.

Respond with ONE Zaphod one-liner only. No explanations. No quotation marks around it. Just the line."""


def load_curated_examples(max: int = 20) -> str:
    """Load the most recent curated examples from examples.json, if it exists."""
    path = os.path.join(os.path.dirname(__file__), "examples.json")
    if not os.path.exists(path):
        return ""
    with open(path) as f:
        examples = json.load(f)
    # Take the most recent `max` entries
    recent = examples[-max:]
    if not recent:
        return ""
    lines = "\n".join(f'- "{e["line"]}"' for e in recent)
    return f"\nCurated examples (use these as style reference):\n{lines}\n"


def call_ollama(context: str, temperature: float = 0.85) -> str | None:
    """
    Hit the local Ollama API and return the generated text.
    Returns None if the call fails or times out.
    """
    if context:
        prompt = (
            f"Situation: {context}\n\n"
            f"Give me the exact words Zaphod Beeblebrox would say out loud in this situation. "
            f"This is a line I will deliver directly to another person. "
            f"First person. Spoken aloud. One sentence or two, max."
        )
    else:
        prompt = "Give me a classic Zaphod Beeblebrox line I can say out loud at a party."

    payload = json.dumps({
        "model":  MODEL,
        "prompt": prompt,
        "system": SYSTEM_PROMPT + load_curated_examples(),
        "stream": False,

        "options": {
            "num_predict": MAX_TOKENS,
            "temperature": temperature,
            "top_p": 0.9,
        }
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as resp:
            data = json.loads(resp.read())
            text = data.get("response", "").strip()
            # Strip surrounding quotes if the model added them
            text = text.strip('"').strip("'").strip()
            return text if text else None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError):
        return None


def get_cached_line() -> str:
    return random.choice(LINE_BANK)


def get_zaphod_line(context: str = "") -> tuple[str, str]:
    """
    Returns (line, source) where source is 'model' or 'cache'.
    """
    line = call_ollama(context)
    if line:
        return line, "model"
    return get_cached_line(), "cache"


def warmup():
    """Pre-load the model into RAM. Run this before the party starts."""
    print(f"Warming up {MODEL} — this may take 15-20s on first run...", flush=True)
    line = call_ollama("say something cool")
    if line:
        print(f"Ready. Test line: {line}")
    else:
        print(f"Warning: model didn't respond within {TIMEOUT_SEC}s. Try increasing TIMEOUT_SEC.")


def interactive():
    """Interactive prompt loop for testing."""
    print(f"Zaphod Beeblebrox — interactive mode  (model: {MODEL})")
    print("Type a prompt and press Enter. Blank line = random cached line. Ctrl-C to quit.\n")
    warmup()
    print()
    while True:
        try:
            context = input("Prompt> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSo long, and thanks for all the fish.")
            break
        line, source = get_zaphod_line(context)
        print(f"Zaphod: {line}\n")


def main():
    if "--warmup" in sys.argv or "--test" in sys.argv:
        warmup()
        return

    if "--interactive" in sys.argv or "-i" in sys.argv:
        interactive()
        return

    context = ""
    if len(sys.argv) > 1:
        context = " ".join(sys.argv[1:])

    line, source = get_zaphod_line(context)
    print(line)


if __name__ == "__main__":
    main()
