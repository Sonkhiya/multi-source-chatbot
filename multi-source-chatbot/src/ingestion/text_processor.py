import hashlib
from typing import List, Tuple
from dataclasses import dataclass
import re


@dataclass
class TextChunk:
    content: str
    start_index: int
    end_index: int


class TextProcessor:
    def __init__(self, chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    
    def chunk_text(self, text: str) -> List[TextChunk]:
        text = self._clean_text(text)
        sentences = self._split_into_sentences(text)
        chunks = self._combine_sentences_into_chunks(sentences)
        return chunks
    
    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        return text
    
    def _split_into_sentences(self, text: str) -> List[str]:
        sentence_endings = r'(?<=[.!?])\s+'
        sentences = re.split(sentence_endings, text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _combine_sentences_into_chunks(self, sentences: List[str]) -> List[TextChunk]:
        chunks = []
        current_chunk = []
        current_length = 0
        char_count = 0
        
        for sentence in sentences:
            sentence_length = len(sentence) + 1
            
            if current_length + sentence_length > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append(chunk_text)
                
                overlap_count = max(1, len(current_chunk) // 2)
                current_chunk = current_chunk[-overlap_count:] if overlap_count > 0 else []
                current_length = sum(len(s) + 1 for s in current_chunk)
            
            current_chunk.append(sentence)
            current_length += sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        
        return [TextChunk(content=chunk, start_index=i, end_index=i) 
                for i, chunk in enumerate(chunks)]
    
    def compute_hash(self, text: str) -> str:
        return hashlib.sha256(text.encode()).hexdigest()
