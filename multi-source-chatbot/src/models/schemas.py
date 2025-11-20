from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class SourceType(str, Enum):
    DOCUMENT = "document"
    WEB_PAGE = "web_page"
    STRUCTURED_RECORD = "structured_record"


class DocumentMetadata(BaseModel):
    document_id: str
    source_type: SourceType
    source_url: Optional[str] = None
    document_name: Optional[str] = None
    record_id: Optional[str] = None
    ingestion_timestamp: datetime
    chunk_index: int
    total_chunks: int
    original_content_hash: str


class DocumentChunk(BaseModel):
    chunk_id: str
    content: str
    metadata: DocumentMetadata
    embedding: Optional[List[float]] = None


class IngestDocumentRequest(BaseModel):
    document_name: str
    file_content: str


class IngestWebPageRequest(BaseModel):
    url: str
    title: Optional[str] = None


class IngestStructuredRecordRequest(BaseModel):
    record_id: str
    data: Dict[str, Any]
    context: Optional[str] = None


class QueryRequest(BaseModel):
    question: str
    session_id: Optional[str] = None
    retrieve_top_k: Optional[int] = None


class Reference(BaseModel):
    source_type: SourceType
    source_url: Optional[str] = None
    document_name: Optional[str] = None
    record_id: Optional[str] = None
    chunk_index: int
    relevance_score: float
    excerpt: str


class QueryResponse(BaseModel):
    query: str
    answer: str
    references: List[Reference]
    confidence_score: float
    response_time_ms: float


class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    vector_store_ready: bool
    model_status: str
