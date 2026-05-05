def build_prompt(context: str, query: str) -> str:
    return f"""
You are an expert AI assistant.

Answer the question using ONLY the information provided below.

Instructions:
- Combine information from all relevant sections.
- Do NOT mention "Context 1", "Source 2", etc.
- Give a clear, direct answer.
- If multiple details exist, synthesize them.
- If the answer is not present, say:
  "I don't have enough information to answer this question."

Context:
{context}

Question:
{query}

Answer:
""".strip()