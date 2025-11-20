from typing import List, Tuple
import numpy as np
from src.storage import VectorStore, EmbeddingService
from src.models import DocumentChunk, Reference, SourceType
from config import settings
from src.logger import logger


class RetrievalEngine:
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
    
    def retrieve(self, query: str, top_k: int = None) -> List[Tuple[DocumentChunk, float]]:
        try:
            top_k = top_k or settings.RETRIEVAL_TOP_K
            
            query_embedding = self.embedding_service.embed_single(query)
            if not query_embedding:
                logger.warning("Failed to generate query embedding")
                return []
            
            query_embedding = np.array(query_embedding)
            chunks = self.vector_store.get_all_chunks()
            
            if not chunks:
                logger.warning("No chunks in vector store")
                return []
            
            embeddings = [chunk.embedding if chunk.embedding else [] for chunk in chunks]
            valid_embeddings = [(i, emb) for i, emb in enumerate(embeddings) if emb]
            
            if not valid_embeddings:
                logger.warning("No valid embeddings in chunks")
                return []
            
            results = self.embedding_service.similarity_search(
                query_embedding,
                [emb for _, emb in valid_embeddings],
                top_k=min(top_k, len(valid_embeddings))
            )
            
            retrieved = []
            for rank, (sim_index, score) in enumerate(results):
                if score >= settings.SIMILARITY_THRESHOLD:
                    actual_index = valid_embeddings[sim_index][0]
                    chunk = chunks[actual_index]
                    retrieved.append((chunk, float(score)))
                    logger.debug(f"Retrieved chunk {rank+1}: score={score:.3f}")
            
            return retrieved
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            return []
    
    def to_references(self, retrieved: List[Tuple[DocumentChunk, float]]) -> List[Reference]:
        references = []
        for chunk, score in retrieved:
            metadata = chunk.metadata
            reference = Reference(
                source_type=metadata.source_type,
                source_url=metadata.source_url,
                document_name=metadata.document_name,
                record_id=metadata.record_id,
                chunk_index=metadata.chunk_index,
                relevance_score=score,
                excerpt=chunk.content[:200]
            )
            references.append(reference)
        return references
