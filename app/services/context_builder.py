from typing import List, Dict


def build_context(
    results: List[Dict],
    max_chunks: int = 5
) -> str:
    """
    Builds structured context from retrieved chunks
    """

    selected = results[:max_chunks]

    context_parts = []

    for i, chunk in enumerate(selected, start=1):
        part = f"[Source {i}]\n{chunk['chunk_text']}\n"
        context_parts.append(part)

    context = "\n\n".join(context_parts)

    return context