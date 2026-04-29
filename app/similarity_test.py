from app.services.embedding_service import EmbeddingService
import json

query = "What is the backend architecture of this system?"

embedding = EmbeddingService.get_embedding(query)

print(len(embedding))      # should be 768

print(json.dumps(embedding))