import requests

OLLAMA_URL = "http://localhost:11434/api/embeddings"
MODEL_NAME = "nomic-embed-text"


class EmbeddingService:

    @staticmethod
    def get_embedding(text: str) -> list[float]:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": text
            }
        )

        if response.status_code != 200:
            raise Exception(response.text)

        return response.json()["embedding"]

    # 🚀 NEW: batch processor
    @staticmethod
    def get_embeddings_batch(texts: list[str], batch_size: int = 10) -> list[list[float]]:
        all_embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]

            batch_embeddings = [
                EmbeddingService.get_embedding(text)
                for text in batch
            ]

            all_embeddings.extend(batch_embeddings)

        return all_embeddings