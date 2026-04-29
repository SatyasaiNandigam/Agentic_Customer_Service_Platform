"""One-shot paraphrase generation script for expanding the intent classification dataset.

Reads eval/datasets/seeds.jsonl, calls gpt-4o-mini to generate 10 paraphrases per seed,
writes a draft JSONL to eval/datasets/intent_classification_draft.jsonl for human review.

Usage:
    python eval/seed_dataset.py
    python eval/seed_dataset.py --seeds eval/datasets/seeds.jsonl --out eval/datasets/draft.jsonl
    python eval/seed_dataset.py --concurrency 5 --paraphrases 10

After running:
1. Open the draft JSONL and delete paraphrases that drift from the intended intent.
2. Merge with hand-authored edge cases.
3. Save final file as eval/datasets/intent_classification.jsonl.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from openai import AsyncOpenAI


_SYSTEM_PROMPT = "You are a dataset generator for an ecommerce customer service classifier."

_USER_TEMPLATE = """\
Generate exactly {n} natural paraphrases of the following customer message.
Each paraphrase must:
- Express the same customer intent (ground truth: "{expected}")
- Use different words, sentence structure, and tone (casual to formal)
- Be realistic — something a real customer would type
- Vary in length: some short (< 8 words), some long (> 20 words)
- Include some with typos or text-speak for variety
- NOT change the intent

Original message: "{text}"

Output as a JSON array of strings only — no markdown fences, no explanation."""


async def generate_paraphrases(
    client: AsyncOpenAI,
    seed_text: str,
    expected_intent: str,
    n: int,
    semaphore: asyncio.Semaphore,
) -> list[str]:
    prompt = _USER_TEMPLATE.format(n=n, expected=expected_intent, text=seed_text)
    async with semaphore:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.9,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
        )
    raw = response.choices[0].message.content or "[]"
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()
    try:
        paraphrases = json.loads(raw)
        if not isinstance(paraphrases, list):
            return []
        return [str(p).strip() for p in paraphrases if str(p).strip()]
    except json.JSONDecodeError:
        print(f"[WARN] Failed to parse paraphrases for: {seed_text[:60]}", file=sys.stderr)
        return []


def load_seeds(path: Path) -> list[dict]:
    seeds = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            seeds.append(json.loads(line))
    return seeds


async def main_async(seeds_path: Path, out_path: Path, concurrency: int, n_paraphrases: int) -> None:
    seeds = load_seeds(seeds_path)
    print(f"Loaded {len(seeds)} seeds from {seeds_path}")

    client = AsyncOpenAI()
    semaphore = asyncio.Semaphore(concurrency)

    all_records: list[dict] = []

    async def process_seed(seed: dict) -> None:
        paraphrases = await generate_paraphrases(
            client, seed["text"], seed["expected"], n_paraphrases, semaphore
        )
        for i, para in enumerate(paraphrases, start=1):
            all_records.append({
                "id": f"{seed['id']}_para_{i:02d}",
                "text": para,
                "expected": seed["expected"],
                "source": "paraphrase",
                "boundary_pair": None,
                "notes": f"paraphrase of {seed['id']}",
            })
        print(f"  {seed['id']}: {len(paraphrases)} paraphrases generated")

    tasks = [process_seed(seed) for seed in seeds]
    await asyncio.gather(*tasks)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        for record in all_records:
            f.write(json.dumps(record) + "\n")

    print(f"\nDraft written to {out_path} ({len(all_records)} records)")
    print("Next: human-review the draft, delete drifted paraphrases, then merge with edge cases.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate paraphrase candidates for the eval dataset.")
    parser.add_argument("--seeds", type=Path, default=Path("eval/datasets/seeds.jsonl"))
    parser.add_argument("--out", type=Path, default=Path("eval/datasets/intent_classification_draft.jsonl"))
    parser.add_argument("--concurrency", type=int, default=5)
    parser.add_argument("--paraphrases", type=int, default=10)
    args = parser.parse_args()

    if not args.seeds.exists():
        print(f"[ERROR] Seeds file not found: {args.seeds}", file=sys.stderr)
        sys.exit(1)

    asyncio.run(main_async(args.seeds, args.out, args.concurrency, args.paraphrases))


if __name__ == "__main__":
    main()
