def build_prompt(context: str, query: str) -> str:
    return f"""
You are a precise AI assistant.

Answer the question using ONLY the information provided in the context below.

- Do NOT use prior knowledge.
- Do NOT make assumptions.
- If the context does not contain the answer, respond with:
  "I don't have enough information to answer this question."

Context:
{context}

Question:
{query}

Answer:
""".strip()