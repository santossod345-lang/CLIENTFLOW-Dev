#!/usr/bin/env python3
"""
Simple CLI to ask the local AI black-box to fix code.
Usage:
  python scripts/ai_assist.py --file backend/somefile.py --instr "Fix failing import and PEP8"

If `AI_PROVIDER` is set to `openai` and `OPENAI_API_KEY` present, it will use OpenAI.
Otherwise it uses the local fallback provider.
"""
import argparse
from backend import ai_module


def main():
    p = argparse.ArgumentParser(description="AI code assistant (local black-box)")
    p.add_argument("--file", required=True, help="Path to file to suggest fixes for")
    p.add_argument("--instr", required=True, help="Instruction for the assistant")
    args = p.parse_args()
    suggestion = ai_module.code_fix_suggestion(args.file, args.instr)
    print(suggestion)


if __name__ == "__main__":
    main()
