from app.services.embedding_service import EmbeddingService

text = "This is a test sentence"

embedding = EmbeddingService.get_embedding(text)

print(len(embedding))  # should be 768
print(embedding[:5])   # preview