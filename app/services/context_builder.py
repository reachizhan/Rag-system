from typing import List, Dict


def build_context(
    results: List[Dict],
    max_chunks: int = 3,
    score_threshold: float = 0.0
) -> str:

    # ✅ Step 1: filter low-quality chunks
    filtered = [r for r in results if r["score"] >= score_threshold]

    # fallback: if everything filtered out, keep top results
    if not filtered:
        filtered = results[:max_chunks]

    # ✅ Step 2: limit number of chunks
    selected = filtered[:max_chunks]

    # ✅ Step 3: format context
    context_parts = []

    for i, chunk in enumerate(selected, start=1):
        part = f"[Source {i}]\n{chunk['chunk_text']}"
        context_parts.append(part)

    # ✅ Step 4: join into single string
    context = "\n\n".join(context_parts)

    return context