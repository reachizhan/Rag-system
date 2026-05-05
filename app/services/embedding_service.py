import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"


class EmbeddingService:

    # ---------------------------------------------------
    # Single embedding
    # ---------------------------------------------------
    @staticmethod
    def get_embedding(text: str) -> List[float]:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": text
            },
            timeout=60  # prevents hanging
        )

        if response.status_code != 200:
            raise Exception(f"Embedding API error: {response.text}")

        data = response.json()

        if "embedding" not in data:
            raise Exception("Invalid response: no embedding field")

        return data["embedding"]

    # ---------------------------------------------------
    # Parallel embeddings (ORDER PRESERVED)
    # ---------------------------------------------------
    @staticmethod
    def get_embeddings_parallel(
        texts: List[str],
        max_workers: int = 5
    ) -> List[List[float]]:

        if not texts:
            return []

        # 🔧 Proper typing (fixes Pylance issue)
        embeddings: List[Optional[List[float]]] = [None] * len(texts)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {
                executor.submit(EmbeddingService.get_embedding, text): idx
                for idx, text in enumerate(texts)
            }

            for future in as_completed(future_to_index):
                idx = future_to_index[future]

                try:
                    result = future.result()
                    embeddings[idx] = result
                except Exception as e:
                    raise Exception(f"Embedding failed at index {idx}: {str(e)}")

        # 🔒 Safety check (important)
        if any(e is None for e in embeddings):
            raise Exception("Some embeddings failed to generate")

        return embeddings  # type: ignore