"""Text chunking strategies for RAG."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any
from dataclasses import dataclass
import tiktoken
from config import settings


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    text: str
    metadata: Dict[str, Any]
    chunk_index: int


class Chunker(ABC):
    """Abstract base class for chunking strategies."""
    
    @abstractmethod
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """Split text into chunks."""
        pass


class FixedSizeChunker(Chunker):
    """Chunk text into fixed-size pieces with overlap."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        encoding_name: str = "cl100k_base"  # GPT-4 encoding
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """Split text into fixed-size chunks with overlap."""
        # Encode text to tokens
        tokens = self.encoding.encode(text)
        
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(tokens):
            # Get chunk tokens
            end = start + self.chunk_size
            chunk_tokens = tokens[start:end]
            
            # Decode back to text
            chunk_text = self.encoding.decode(chunk_tokens)
            
            # Create chunk with metadata
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = chunk_index
            chunk_metadata['start_char'] = start
            chunk_metadata['end_char'] = end
            
            chunks.append(TextChunk(
                text=chunk_text,
                metadata=chunk_metadata,
                chunk_index=chunk_index
            ))
            
            # Move to next chunk with overlap
            start += self.chunk_size - self.chunk_overlap
            chunk_index += 1
        
        return chunks


class SemanticChunker(Chunker):
    """Chunk text based on semantic boundaries (paragraphs, sections)."""
    
    def __init__(
        self,
        max_chunk_size: int = None,
        encoding_name: str = "cl100k_base"
    ):
        self.max_chunk_size = max_chunk_size or settings.chunk_size
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """Split text based on paragraphs/sections."""
        # Split by double newlines (paragraphs)
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            para_tokens = len(self.encoding.encode(para))
            
            # If paragraph itself is too large, split it
            if para_tokens > self.max_chunk_size:
                # Flush current chunk if any
                if current_chunk:
                    chunk_text = '\n\n'.join(current_chunk)
                    chunk_metadata = metadata.copy()
                    chunk_metadata['chunk_index'] = chunk_index
                    chunks.append(TextChunk(chunk_text, chunk_metadata, chunk_index))
                    chunk_index += 1
                    current_chunk = []
                    current_size = 0
                
                # Split large paragraph using fixed chunker
                fixed_chunker = FixedSizeChunker(self.max_chunk_size, 100)
                para_chunks = fixed_chunker.chunk(para, metadata)
                for pc in para_chunks:
                    pc.chunk_index = chunk_index
                    chunks.append(pc)
                    chunk_index += 1
                continue
            
            # Check if adding this paragraph exceeds max size
            if current_size + para_tokens > self.max_chunk_size and current_chunk:
                # Create chunk from accumulated paragraphs
                chunk_text = '\n\n'.join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = chunk_index
                chunks.append(TextChunk(chunk_text, chunk_metadata, chunk_index))
                chunk_index += 1
                
                # Start new chunk
                current_chunk = [para]
                current_size = para_tokens
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_size += para_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '\n\n'.join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = chunk_index
            chunks.append(TextChunk(chunk_text, chunk_metadata, chunk_index))
        
        return chunks


class RecursiveChunker(Chunker):
    """Recursively chunk text using multiple separators."""
    
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
        separators: List[str] = None,
        encoding_name: str = "cl100k_base"
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]
        self.encoding = tiktoken.get_encoding(encoding_name)
    
    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Recursively split text using separators."""
        if not separators or not text:
            return [text] if text else []
        
        separator = separators[0]
        remaining_separators = separators[1:]
        
        # Handle empty separator - just return the text as-is
        if separator == "":
            return [text]
        
        splits = text.split(separator)
        
        # If only one split, try next separator
        if len(splits) == 1:
            if remaining_separators:
                return self._split_text(text, remaining_separators)
            return [text]
        
        # Recursively split each part (but skip empty separator in recursion)
        result = []
        non_empty_separators = [s for s in remaining_separators if s != ""]
        for split in splits:
            if split:
                if non_empty_separators:
                    result.extend(self._split_text(split, non_empty_separators))
                else:
                    result.append(split)
        
        return result if result else [text]
    
    def chunk(self, text: str, metadata: Dict[str, Any]) -> List[TextChunk]:
        """Chunk text recursively."""
        splits = self._split_text(text, self.separators)
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_index = 0
        
        for split in splits:
            split_tokens = len(self.encoding.encode(split))
            
            if current_size + split_tokens > self.chunk_size and current_chunk:
                # Create chunk
                chunk_text = " ".join(current_chunk)
                chunk_metadata = metadata.copy()
                chunk_metadata['chunk_index'] = chunk_index
                chunks.append(TextChunk(chunk_text, chunk_metadata, chunk_index))
                chunk_index += 1
                
                # Keep overlap
                overlap_size = 0
                overlap_parts = []
                for part in reversed(current_chunk):
                    part_size = len(self.encoding.encode(part))
                    if overlap_size + part_size <= self.chunk_overlap:
                        overlap_parts.insert(0, part)
                        overlap_size += part_size
                    else:
                        break
                
                current_chunk = overlap_parts + [split]
                current_size = overlap_size + split_tokens
            else:
                current_chunk.append(split)
                current_size += split_tokens
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunk_metadata = metadata.copy()
            chunk_metadata['chunk_index'] = chunk_index
            chunks.append(TextChunk(chunk_text, chunk_metadata, chunk_index))
        
        return chunks


# Default chunker factory
def get_chunker(strategy: str = "recursive") -> Chunker:
    """Get a chunker instance based on strategy name."""
    chunkers = {
        "fixed": FixedSizeChunker,
        "semantic": SemanticChunker,
        "recursive": RecursiveChunker
    }
    
    chunker_class = chunkers.get(strategy, RecursiveChunker)
    return chunker_class()
