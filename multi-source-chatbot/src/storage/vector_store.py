import pickle
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from config import settings
from src.models import DocumentChunk, DocumentMetadata, SourceType
from src.logger import logger


class VectorStore:
    def __init__(self, store_path: str = None):
        self.store_path = Path(store_path or settings.VECTOR_STORE_PATH)
        self.store_path.mkdir(parents=True, exist_ok=True)
        self.chunks_file = self.store_path / "chunks.pkl"
        self.metadata_file = self.store_path / "metadata.json"
        self.chunks: List[DocumentChunk] = []
        self.metadata_index: Dict[str, Dict[str, Any]] = {}
        self._load()
    
    def _load(self):
        try:
            if self.chunks_file.exists():
                with open(self.chunks_file, 'rb') as f:
                    self.chunks = pickle.load(f)
                logger.info(f"Loaded {len(self.chunks)} chunks from store")
            
            if self.metadata_file.exists():
                with open(self.metadata_file, 'r') as f:
                    self.metadata_index = json.load(f)
        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            self.chunks = []
            self.metadata_index = {}
    
    def _save(self):
        try:
            with open(self.chunks_file, 'wb') as f:
                pickle.dump(self.chunks, f)
            
            with open(self.metadata_file, 'w') as f:
                json.dump(self.metadata_index, f, indent=2, default=str)
            
            logger.debug("Vector store persisted")
        except Exception as e:
            logger.error(f"Error saving vector store: {e}")
    
    def add_chunks(self, chunks: List[DocumentChunk], source_id: str):
        try:
            for chunk in chunks:
                chunk.chunk_id = str(uuid.uuid4())
                self.chunks.append(chunk)
            
            self.metadata_index[source_id] = {
                "chunk_count": len(chunks),
                "added_at": datetime.now().isoformat(),
                "chunk_ids": [chunk.chunk_id for chunk in chunks]
            }
            
            self._save()
            logger.info(f"Added {len(chunks)} chunks for source {source_id}")
        except Exception as e:
            logger.error(f"Error adding chunks: {e}")
            raise
    
    def get_all_chunks(self) -> List[DocumentChunk]:
        return self.chunks
    
    def get_chunks_by_source(self, source_id: str) -> List[DocumentChunk]:
        if source_id not in self.metadata_index:
            return []
        
        chunk_ids = self.metadata_index[source_id].get("chunk_ids", [])
        return [c for c in self.chunks if c.chunk_id in chunk_ids]
    
    def delete_source(self, source_id: str):
        try:
            if source_id not in self.metadata_index:
                return
            
            chunk_ids = self.metadata_index[source_id].get("chunk_ids", [])
            self.chunks = [c for c in self.chunks if c.chunk_id not in chunk_ids]
            del self.metadata_index[source_id]
            self._save()
            logger.info(f"Deleted source {source_id}")
        except Exception as e:
            logger.error(f"Error deleting source: {e}")
            raise
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_chunks": len(self.chunks),
            "total_sources": len(self.metadata_index),
            "store_size_mb": self.chunks_file.stat().st_size / (1024 * 1024) if self.chunks_file.exists() else 0
        }
