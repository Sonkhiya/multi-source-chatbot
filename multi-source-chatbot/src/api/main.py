from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time
from datetime import datetime
from config import settings
from src.logger import logger, query_logger
from src.models import (
    IngestDocumentRequest,
    IngestWebPageRequest,
    IngestStructuredRecordRequest,
    QueryRequest,
    QueryResponse,
    HealthCheckResponse,
    Reference
)
from src.storage import VectorStore, EmbeddingService
from src.retrieval import RetrievalEngine
from src.ingestion import IngestionManager
from src.agent import QueryGraphBuilder, LLMService


settings.ensure_dirs()

vector_store: VectorStore = None
embedding_service: EmbeddingService = None
retrieval_engine: RetrievalEngine = None
ingestion_manager: IngestionManager = None
query_graph: QueryGraphBuilder = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global vector_store, embedding_service, retrieval_engine, ingestion_manager, query_graph
    
    try:
        logger.info("Initializing chatbot system...")
        
        vector_store = VectorStore()
        embedding_service = EmbeddingService()
        retrieval_engine = RetrievalEngine(vector_store, embedding_service)
        ingestion_manager = IngestionManager(vector_store, embedding_service)
        
        llm_service = LLMService(
            model_name=settings.GEMINI_MODEL,
            temperature=settings.LLM_TEMPERATURE
        )
        query_graph = QueryGraphBuilder(retrieval_engine, llm_service)
        
        logger.info("Chatbot system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize chatbot system: {e}")
        raise
    
    yield
    
    logger.info("Shutting down chatbot system")


app = FastAPI(
    title="Multi-Source Chatbot",
    description="A production-ready chatbot with multi-source ingestion",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    try:
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now(),
            vector_store_ready=vector_store is not None and len(vector_store.get_all_chunks()) >= 0,
            model_status="ready" if query_graph else "not_ready"
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service unhealthy")


@app.post("/ingest/document")
async def ingest_document(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None
):
    try:
        if not file.filename:
            raise HTTPException(status_code=400, detail="File name required")
        
        content = await file.read()
        
        if not content:
            raise HTTPException(status_code=400, detail="File is empty")
        
        document_id = await ingestion_manager.ingest_document(file.filename, content)
        
        logger.info(f"Document ingestion initiated: {file.filename} (ID: {document_id})")
        
        return {
            "status": "success",
            "document_id": document_id,
            "filename": file.filename,
            "message": "Document ingested and indexed successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting document: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/webpage")
async def ingest_webpage(request: IngestWebPageRequest):
    try:
        if not request.url:
            raise HTTPException(status_code=400, detail="URL required")
        
        webpage_id = await ingestion_manager.ingest_webpage(request.url, request.title)
        
        logger.info(f"Webpage ingestion initiated: {request.url} (ID: {webpage_id})")
        
        return {
            "status": "success",
            "webpage_id": webpage_id,
            "url": request.url,
            "message": "Webpage fetched, indexed successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting webpage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ingest/record")
async def ingest_structured_record(request: IngestStructuredRecordRequest):
    try:
        if not request.record_id:
            raise HTTPException(status_code=400, detail="Record ID required")
        
        record_source_id = await ingestion_manager.ingest_structured_record(
            request.record_id,
            request.data,
            request.context
        )
        
        logger.info(f"Record ingestion initiated: {request.record_id} (ID: {record_source_id})")
        
        return {
            "status": "success",
            "source_id": record_source_id,
            "record_id": request.record_id,
            "message": "Structured record indexed successfully"
        }
    except Exception as e:
        logger.error(f"Error ingesting record: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    try:
        if not request.question or len(request.question.strip()) == 0:
            raise HTTPException(status_code=400, detail="Question required")
        
        start_time = time.time()
        
        result = query_graph.process_query(request.question)
        
        response_time_ms = (time.time() - start_time) * 1000
        
        query_logger.info(
            f"Query: {request.question} | Answer length: {len(result['answer'])} | "
            f"References: {len(result['references'])} | Confidence: {result['confidence_score']:.2f}"
        )
        
        if result.get('error'):
            raise HTTPException(status_code=500, detail=result['error'])
        
        return QueryResponse(
            query=request.question,
            answer=result['answer'],
            references=result['references'],
            confidence_score=result['confidence_score'],
            response_time_ms=response_time_ms
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail="Failed to process query")


@app.get("/stats")
async def get_stats():
    try:
        stats = ingestion_manager.get_ingestion_stats()
        return {
            "status": "success",
            "ingestion_stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level=settings.LOG_LEVEL.lower()
    )
