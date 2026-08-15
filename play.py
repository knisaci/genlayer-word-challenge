#!/usr/bin/env python3
"""
Word Challenge — CLI Player
Contract: 0x621326E5faE3c5dEe52171E14Eff9DC4741138c1
Network:  Testnet Bradbury
"""

import subprocess
import json
import sys

CONTRACT = "0x621326E5faE3c5dEe52171E14Eff9DC4741138c1"

def run(cmd):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return result.stdout.strip()

def get_word():
    out = run(f"genlayer call {CONTRACT} get_today_word")
    for line in out.splitlines():
        line = line.strip()
        if line and not line.startswith("[") and not line.startswith("�") and not line.startswith("✔") and not line.startswith("Result:") and not line.startswith("Calling"):
            return line
    return "unknown"

def get_stats(address):
    out = run(f'genlayer call {CONTRACT} get_player_stats --args \'["{address}"]\'')
    for line in out.splitlines():
        line = line.strip()
        if line.startswith("{"):
            try:
                return json.loads(line)
            except:
                pass
    return {"score": 0, "streak": 0, "history": []}

def submit(sentence):
    out = run(f'genlayer write {CONTRACT} submit_sentence --args \'["{sentence}"]\'')
    return out

def main():
    print("\n🟢 Word Challenge — Testnet Bradbury")
    print("=" * 40)

    word = get_word()
    print(f"\n📝 Today's word: {word.upper()}\n")
    print("Write one sentence using this word correctly.")
    print("Validators will judge correctness and creativity.\n")

    sentence = input("Your sentence: ").strip()
    if not sentence:
        print("No sentence entered. Exiting.")
        sys.exit(0)

    print("\n⏳ Submitting to Bradbury validators... (~30-60s)\n")
    result = submit(sentence)
    print(result)
    print("\n✅ Done. Run the script again to play another round.")

if __name__ == "__main__":
    main()
