from langgraph.graph import StateGraph, START, END
from typing import Any
from datetime import datetime
from src.agent.llm_service import AgentState, ContextAugmenter, LLMService
from src.retrieval import RetrievalEngine
from src.logger import logger


class QueryGraphBuilder:
    def __init__(self, retrieval_engine: RetrievalEngine, llm_service: LLMService):
        self.retrieval_engine = retrieval_engine
        self.llm_service = llm_service
        self.graph = None
        self._build_graph()
    
    def _build_graph(self):
        workflow = StateGraph(AgentState)
        
        workflow.add_node("retrieve", self._retrieve_node)
        workflow.add_node("format_context", self._format_context_node)
        workflow.add_node("generate_answer", self._generate_answer_node)
        workflow.add_node("finalize", self._finalize_node)
        
        workflow.add_edge(START, "retrieve")
        workflow.add_edge("retrieve", "format_context")
        workflow.add_edge("format_context", "generate_answer")
        workflow.add_edge("generate_answer", "finalize")
        workflow.add_edge("finalize", END)
        
        self.graph = workflow.compile()
    
    def _retrieve_node(self, state: AgentState) -> AgentState:
        try:
            logger.info(f"Retrieving context for query: {state['query']}")
            retrieved = self.retrieval_engine.retrieve(state['query'])
            references = self.retrieval_engine.to_references(retrieved)
            state['references'] = references
            logger.info(f"Retrieved {len(references)} relevant chunks")
        except Exception as e:
            logger.error(f"Error in retrieve node: {e}")
            state['error'] = str(e)
        
        return state
    
    def _format_context_node(self, state: AgentState) -> AgentState:
        try:
            context = ContextAugmenter.format_context(state['references'])
            state['retrieved_context'] = context
        except Exception as e:
            logger.error(f"Error in format_context node: {e}")
            state['error'] = str(e)
        
        return state
    
    def _generate_answer_node(self, state: AgentState) -> AgentState:
        try:
            prompt = ContextAugmenter.build_prompt(
                state['query'],
                state['retrieved_context']
            )
            answer = self.llm_service.generate_answer(prompt)
            state['answer'] = answer
            state['confidence_score'] = self.llm_service.estimate_confidence(state['references'])
        except Exception as e:
            logger.error(f"Error in generate_answer node: {e}")
            state['error'] = str(e)
            state['answer'] = "Sorry, I encountered an error while generating an answer."
        
        return state
    
    def _finalize_node(self, state: AgentState) -> AgentState:
        logger.info(f"Query processed with {len(state['references'])} references")
        return state
    
    def process_query(self, query: str) -> AgentState:
        initial_state = AgentState(
            query=query,
            retrieved_context="",
            references=[],
            answer="",
            confidence_score=0.0,
            error=None
        )
        
        result = self.graph.invoke(initial_state)
        return result
