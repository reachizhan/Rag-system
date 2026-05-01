def build_prompt(context: str, query: str) -> str:
    return f"""
You are a precise AI assistant.

Answer the question using ONLY the information provided in the context below.

Instructions:
- Carefully read ALL sources before answering.
- Prefer the most direct and relevant definition.
- Do NOT pick the first matching sentence.
- Ignore unrelated details.
- If multiple sources conflict, choose the most relevant one.

If the context does not contain the answer, respond with:
"I don't have enough information to answer this question."

Context:
{context}

Question:
{query}

Answer:
""".strip()