#!/usr/bin/env python3
"""
Zaphod Line Curator
Generate 5 one-liners from a prompt, pick the best ones or refine all 5, save to examples.json.
The bot automatically loads these examples on every run.

Usage:  python curator.py
"""

import json
import os
import re
import sys
import urllib.request
from zaphod_local import get_cached_line, OLLAMA_URL, SYSTEM_PROMPT, load_curated_examples, MODEL

EXAMPLES_FILE = os.path.join(os.path.dirname(__file__), "examples.json")


# ---------------------------------------------------------------------------
# Examples file
# ---------------------------------------------------------------------------

def load_examples() -> list[dict]:
    if os.path.exists(EXAMPLES_FILE):
        with open(EXAMPLES_FILE) as f:
            return json.load(f)
    return []


def save_example(prompt: str, line: str):
    examples = load_examples()
    examples.append({"prompt": prompt, "line": line})
    with open(EXAMPLES_FILE, "w") as f:
        json.dump(examples, f, indent=2)
    print(f"  Saved. ({len(examples)} examples total)")


# ---------------------------------------------------------------------------
# Generate 5 lines
# ---------------------------------------------------------------------------

def generate_five(prompt: str, note: str = "") -> list[str]:
    """Single call asking for 5 numbered variations.
    If `note` is provided, it's appended as a refinement instruction.
    """
    multi_prompt = (
        f"Situation: {prompt}\n\n"
        f"Give me 5 different one-liners Zaphod Beeblebrox would say in this situation. "
        f"Each must be distinctly different in approach — vary between charming, dismissive, "
        f"self-aggrandising, witty, and outrageous. "
        f"These are lines spoken directly TO another person. First person. No narration.\n\n"
    )

    if note:
        multi_prompt += f"Additional note: {note}\n\n"

    multi_prompt += (
        f"Format exactly as:\n"
        f"1. [line]\n2. [line]\n3. [line]\n4. [line]\n5. [line]"
    )

    payload = json.dumps({
        "model":  MODEL,
        "prompt": multi_prompt,
        "system": SYSTEM_PROMPT + load_curated_examples(),
        "stream": False,
        "options": {"num_predict": 300, "temperature": 0.95, "top_p": 0.95},
    }).encode()

    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    print("\n  Generating", end="", flush=True)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            print("  done")
            raw = data.get("response", "")
            lines = re.findall(r"^\d+[.)]\s*(.+)$", raw, re.MULTILINE)
            lines = [l.strip().strip('"').strip("'") for l in lines if l.strip()]
            if lines:
                return lines[:5]
    except Exception:
        print("  (model unavailable)")

    return [get_cached_line() for _ in range(5)]


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

def print_header():
    print("\n" + "=" * 58)
    print("  ZAPHOD BEEBLEBROX — Line Curator")
    print(f"  model: {MODEL}   examples: {EXAMPLES_FILE}")
    print("=" * 58)


def run():
    print_header()
    examples = load_examples()
    print(f"  {len(examples)} curated examples loaded.\n")

    while True:
        # --- get prompt ---
        try:
            prompt = input("Prompt (or 'q' to quit): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nSo long, and thanks for all the fish.")
            break

        if prompt.lower() in ("q", "quit", "exit"):
            print("So long, and thanks for all the fish.")
            break
        if not prompt:
            continue

        lines = generate_five(prompt)

        while True:
            # --- display ---
            print()
            for i, line in enumerate(lines, 1):
                print(f"  {i}.  {line}")
            print()
            print("  Enter number(s) to save  (e.g. 1 3)")
            print("  Enter a note to regenerate all 5  (e.g. 'more tongue in cheek')")
            print("  r = regenerate as-is   q = new prompt")
            print()

            try:
                choice = input("> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nSo long, and thanks for all the fish.")
                sys.exit(0)

            if not choice:
                continue

            if choice.lower() in ("q", "quit"):
                break

            if choice.lower() == "r":
                lines = generate_five(prompt)
                continue

            # Check if input is purely numbers (save) or text (refine)
            tokens = choice.replace(",", " ").split()
            if all(t.isdigit() for t in tokens):
                # Save selected lines
                picks = [int(t) for t in tokens if 1 <= int(t) <= len(lines)]
                if picks:
                    for n in picks:
                        save_example(prompt, lines[n - 1])
                        print(f"  Added: \"{lines[n - 1]}\"")
                    print()
                else:
                    print("  No valid line numbers. Try again.")
            else:
                # Treat as a refinement note — regenerate all 5
                lines = generate_five(prompt, note=choice)


if __name__ == "__main__":
    run()
