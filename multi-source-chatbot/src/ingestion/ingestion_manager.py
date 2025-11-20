import uuid
from datetime import datetime
from typing import List
import asyncio
from src.ingestion import (
    TextProcessor,
    DocumentProcessor,
    WebPageProcessor,
    StructuredDataProcessor
)
from src.storage import VectorStore, EmbeddingService
from src.models import DocumentChunk, DocumentMetadata, SourceType
from src.logger import logger


class IngestionManager:
    def __init__(self, vector_store: VectorStore, embedding_service: EmbeddingService):
        self.vector_store = vector_store
        self.embedding_service = embedding_service
        self.text_processor = TextProcessor()
    
    async def ingest_document(self, document_name: str, file_content: bytes) -> str:
        try:
            logger.info(f"Ingesting document: {document_name}")
            
            text = DocumentProcessor.detect_and_extract(document_name, file_content)
            document_id = str(uuid.uuid4())
            
            chunks = await self._process_and_chunk(
                text,
                document_id,
                SourceType.DOCUMENT,
                document_name=document_name
            )
            
            self.vector_store.add_chunks(chunks, document_id)
            logger.info(f"Document ingested: {document_id} with {len(chunks)} chunks")
            return document_id
        except Exception as e:
            logger.error(f"Error ingesting document: {e}")
            raise
    
    async def ingest_webpage(self, url: str, title: str = None) -> str:
        try:
            logger.info(f"Ingesting webpage: {url}")
            
            text = await WebPageProcessor.fetch_and_extract(url)
            webpage_id = str(uuid.uuid4())
            
            chunks = await self._process_and_chunk(
                text,
                webpage_id,
                SourceType.WEB_PAGE,
                source_url=url,
                title=title or url
            )
            
            self.vector_store.add_chunks(chunks, webpage_id)
            logger.info(f"Webpage ingested: {webpage_id} with {len(chunks)} chunks")
            return webpage_id
        except Exception as e:
            logger.error(f"Error ingesting webpage: {e}")
            raise
    
    async def ingest_structured_record(self, record_id: str, data: dict, context: str = None) -> str:
        try:
            logger.info(f"Ingesting structured record: {record_id}")
            
            text = StructuredDataProcessor.validate_and_flatten(data, context)
            source_id = str(uuid.uuid4())
            
            chunks = await self._process_and_chunk(
                text,
                source_id,
                SourceType.STRUCTURED_RECORD,
                record_id=record_id
            )
            
            self.vector_store.add_chunks(chunks, source_id)
            logger.info(f"Structured record ingested: {source_id} with {len(chunks)} chunks")
            return source_id
        except Exception as e:
            logger.error(f"Error ingesting structured record: {e}")
            raise
    
    async def _process_and_chunk(
        self,
        text: str,
        source_id: str,
        source_type: SourceType,
        **metadata_kwargs
    ) -> List[DocumentChunk]:
        text_chunks = self.text_processor.chunk_text(text)
        content_hash = self.text_processor.compute_hash(text)
        
        embeddings = self.embedding_service.embed([chunk.content for chunk in text_chunks])
        
        document_chunks = []
        for idx, (text_chunk, embedding) in enumerate(zip(text_chunks, embeddings)):
            metadata = DocumentMetadata(
                document_id=source_id,
                source_type=source_type,
                ingestion_timestamp=datetime.now(),
                chunk_index=idx,
                total_chunks=len(text_chunks),
                original_content_hash=content_hash,
                **metadata_kwargs
            )
            
            chunk = DocumentChunk(
                chunk_id="",
                content=text_chunk.content,
                metadata=metadata,
                embedding=embedding.tolist() if hasattr(embedding, 'tolist') else embedding
            )
            document_chunks.append(chunk)
        
        return document_chunks
    
    def get_ingestion_stats(self) -> dict:
        return self.vector_store.get_stats()
