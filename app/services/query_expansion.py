from app.services.llm_service import generate_answer
import re


def expand_query_llm(query: str):
    """
    Use LLM to generate better search queries
    """

    prompt = f"""
You are a query rewriting system for semantic search.

Generate exactly 1 alternative search queries.

CRITICAL RULES:
- Output ONLY the 1 queries
- NO explanations
- NO headings
- NO labels
- NO introductory text
- NO phrases like "Here are", "queries:", "alternatives"
- Each line must be a clean query only

Rules for queries:
- Must preserve original meaning
- Must be short and search-friendly
- Must not include formatting or commentary

User query:
{query}
"""

    response = generate_answer(prompt)

    queries = []

    for line in response.split("\n"):
        line = line.strip()
        if not line:
            continue

        # 🔥 Remove numbering like "1. ", "2) ", etc.
        line = re.sub(r"^\d+[\).\s]+", "", line)

        queries.append(line)

    # 🔥 Always include original query
    final_queries = [query] + queries[:3]

    return final_queries