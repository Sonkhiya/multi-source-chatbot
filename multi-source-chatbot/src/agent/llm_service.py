from typing import TypedDict, Optional, List
import json
from datetime import datetime
from langchain_google_genai import ChatGoogleGenerativeAI
from src.models import Reference
from config import settings
from src.logger import logger


class AgentState(TypedDict):
    query: str
    retrieved_context: str
    references: List[Reference]
    answer: str
    confidence_score: float
    error: Optional[str]


class ContextAugmenter:
    @staticmethod
    def format_context(references: List[Reference]) -> str:
        if not references:
            return "No relevant context found."
        
        # Limit to top 3 references to reduce payload size
        limited_refs = references[:3]
        
        context = "Based on the following sources:\n\n"
        for i, ref in enumerate(limited_refs, 1):
            source_info = ContextAugmenter._format_reference(ref)
            context += f"{i}. {source_info}\n"
            # Reduce excerpt to 100 characters instead of 150
            context += f"   {ref.excerpt[:100]}\n\n"
        
        return context
    
    @staticmethod
    def _format_reference(ref: Reference) -> str:
        if ref.source_type.value == "document":
            return f"Document: {ref.document_name} (Relevance: {ref.relevance_score:.2%})"
        elif ref.source_type.value == "web_page":
            return f"Web Page: {ref.source_url} (Relevance: {ref.relevance_score:.2%})"
        else:
            return f"Record: {ref.record_id} (Relevance: {ref.relevance_score:.2%})"
    
    @staticmethod
    def build_prompt(query: str, context: str) -> str:
        return f"""You are a helpful and accurate information assistant. 

User Question: {query}

Context Information:
{context}

Please provide a clear and comprehensive answer based on the context provided. 
If the context doesn't contain relevant information, say so clearly.
Format your response in a structured way with clear paragraphs.
"""


class LLMService:
    def __init__(self, gemini_api_key: str = None, model_name: str = None, temperature: float = None):
        if not gemini_api_key:
            gemini_api_key = settings.GEMINI_API_KEY
            if not gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set. Please set it in .env file")
        
        self.gemini_api_key = gemini_api_key
        self.model_name = model_name or settings.GEMINI_MODEL
        self.temperature = temperature if temperature is not None else settings.LLM_TEMPERATURE
        
        self._initialize_llm()
    
    def _initialize_llm(self):
        try:
            logger.info(f"Initializing Gemini LLM with model: {self.model_name}")
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=self.gemini_api_key,
                model=self.model_name,
                temperature=self.temperature,
                max_output_tokens=settings.MAX_TOKENS
            )
            logger.info("Gemini LLM initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Gemini LLM: {e}")
            raise
    
    def generate_answer(self, prompt: str) -> str:
        try:
            from langchain_core.messages import HumanMessage
            message = HumanMessage(content=prompt)
            response = self.llm.invoke([message])
            return response.content
        except Exception as e:
            logger.error(f"Error generating answer with Gemini: {e}")
            raise RuntimeError(f"Error generating answer: {e}")
    
    def estimate_confidence(self, references: List[Reference]) -> float:
        if not references:
            return 0.0
        
        avg_relevance = sum(ref.relevance_score for ref in references) / len(references)
        confidence = min(avg_relevance * 1.2, 1.0)
        return confidence
