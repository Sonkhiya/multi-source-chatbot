from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from config import settings
from src.logger import logger


class EmbeddingService:
    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.EMBEDDING_MODEL
        self.model = None
        self._initialize()
    
    def _initialize(self):
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def embed(self, texts: List[str]) -> np.ndarray:
        if not self.model:
            raise RuntimeError("Embedding model not initialized")
        
        try:
            embeddings = self.model.encode(texts, convert_to_tensor=False)
            return embeddings
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            raise
    
    def embed_single(self, text: str) -> List[float]:
        embeddings = self.embed([text])
        return embeddings[0].tolist() if len(embeddings) > 0 else []
    
    def similarity_search(self, query_embedding: np.ndarray, embeddings: List[List[float]], top_k: int = 5) -> List[tuple]:
        try:
            embeddings_array = np.array(embeddings)
            similarities = np.dot(embeddings_array, query_embedding) / (
                np.linalg.norm(embeddings_array, axis=1) * np.linalg.norm(query_embedding) + 1e-8
            )
            
            top_indices = np.argsort(similarities)[::-1][:top_k]
            top_scores = similarities[top_indices]
            
            return list(zip(top_indices, top_scores))
        except Exception as e:
            logger.error(f"Error computing similarity: {e}")
            raise
