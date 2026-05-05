from typing import List, Dict

def build_context(results, max_parents=3):
    seen = set()
    context_parts = []

    for r in results:
        pid = r["parent_id"]

        if pid in seen:
            continue

        seen.add(pid)

        part = f"""
[Relevant Section]
{r['parent_text']}
"""
        context_parts.append(part.strip())

        if len(context_parts) >= max_parents:
            break

    return "\n\n---\n\n".join(context_parts)