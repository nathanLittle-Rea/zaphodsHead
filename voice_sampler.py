#!/usr/bin/env python3
"""
Voice sampler — audition macOS `say` voices for Zaphod's Head.
Plays a test line through each candidate voice, lets you pick the best one,
and writes your choice into tts.py.

Usage: python voice_sampler.py
"""

import subprocess
import sys

TEST_LINE = (
    "I'm Zaphod Beeblebrox — yes, both of me. "
    "I stole the most incredible ship in the galaxy. "
    "It seemed like the right call at the time."
)

# Curated shortlist — British males first, then wildcards worth hearing
CANDIDATES = [
    ("Daniel",               "en_GB", "British male — the obvious choice"),
    ("Reed (English (UK))",  "en_GB", "British male — younger, crisper"),
    ("Eddy (English (UK))",  "en_GB", "British male — warmer"),
    ("Rocko (English (UK))", "en_GB", "British male — rougher"),
    ("Grandpa (English (UK))","en_GB","British male — older, distinguished"),
    ("Ralph",                "en_US", "Nasal, world-weary"),
    ("Fred",                 "en_US", "Classic robotic — retro sci-fi"),
    ("Jester",               "en_US", "Cocky, exaggerated"),
    ("Superstar",            "en_US", "Smooth, self-important"),
    ("Zarvox",               "en_US", "Alien robot — wildcard"),
    ("Bad News",             "en_US", "Deadpan doom — very Marvin, but worth hearing"),
]


def play(voice: str, text: str):
    subprocess.run(["say", "-v", voice, text], check=True)


def write_voice_to_tts(voice: str):
    """Update the MACOS_VOICE constant in tts.py."""
    import re
    with open("tts.py") as f:
        content = f.read()

    # Replace or insert the MACOS_VOICE line
    new_line = f'MACOS_VOICE   = "{voice}"'
    if "MACOS_VOICE" in content:
        content = re.sub(r'^MACOS_VOICE\s*=.*$', new_line, content, flags=re.MULTILINE)
    else:
        # Insert after PIPER_MODEL line
        content = content.replace(
            'PIPER_MODEL  =',
            f'{new_line}\nPIPER_MODEL  ='
        )

    with open("tts.py", "w") as f:
        f.write(content)

    print(f"\n  tts.py updated — MACOS_VOICE = \"{voice}\"")


def run():
    print("\n" + "=" * 58)
    print("  ZAPHOD'S HEAD — Voice Sampler")
    print("=" * 58)
    print(f'\n  Test line: "{TEST_LINE}"\n')
    print("  Press Enter to play each voice. Skip with 's', quit with 'q'.\n")

    heard = []

    for i, (voice, locale, note) in enumerate(CANDIDATES, 1):
        print(f"  {i:2}.  {voice:<28} {locale}  — {note}")
        try:
            cmd = input("       [Enter to play / s to skip / q to quit] ").strip().lower()
        except (KeyboardInterrupt, EOFError):
            break

        if cmd == "q":
            break
        if cmd == "s":
            continue

        try:
            play(voice, TEST_LINE)
            heard.append((i, voice, note))
        except Exception as e:
            print(f"       (error: {e})")

    if not heard:
        print("\n  Nothing heard. Run again when you're ready.")
        return

    print("\n" + "-" * 58)
    print("  Voices you heard:")
    for i, voice, note in heard:
        print(f"    {i}.  {voice}  — {note}")
    print()

    try:
        pick = input("  Enter the number of your favourite (or Enter to skip): ").strip()
    except (KeyboardInterrupt, EOFError):
        return

    if not pick.isdigit():
        print("  No changes made.")
        return

    idx = int(pick) - 1
    if 0 <= idx < len(CANDIDATES):
        chosen_voice = CANDIDATES[idx][0]
        write_voice_to_tts(chosen_voice)
        print(f"\n  Playing final selection: {chosen_voice}\n")
        play(chosen_voice, TEST_LINE)
    else:
        print("  Invalid choice. No changes made.")


if __name__ == "__main__":
    run()
