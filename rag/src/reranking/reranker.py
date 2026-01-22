"""Cross-encoder reranking for improved retrieval precision."""

from dataclasses import dataclass, field
from typing import Optional
import logging

import numpy as np
from sentence_transformers import CrossEncoder

logger = logging.getLogger(__name__)


@dataclass
class RerankerConfig:
    """Configuration for cross-encoder reranking."""
    
    model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    batch_size: int = 32
    device: str = "cpu"  # "cpu", "cuda", "mps"
    normalize_scores: bool = True


@dataclass
class RankedResult:
    """A reranked search result with cross-encoder score."""
    
    text: str
    chunk_id: str
    source_path: str
    original_score: float  # Vector similarity score
    rerank_score: float    # Cross-encoder relevance score
    chunk_index: int = 0
    token_count: int = 0
    metadata: dict = field(default_factory=dict)
    
    @property
    def combined_score(self) -> float:
        """Combined score using rerank as primary."""
        return self.rerank_score


class Reranker:
    """
    Cross-encoder reranker for improving retrieval precision.
    
    Cross-encoders process (query, document) pairs jointly, 
    capturing deeper semantic relationships than bi-encoders.
    Use after initial retrieval to rerank top-K candidates.
    """
    
    def __init__(self, config: RerankerConfig | None = None):
        self.config = config or RerankerConfig()
        self.model = CrossEncoder(
            self.config.model_name,
            device=self.config.device,
        )
    
    def rerank(
        self,
        query: str,
        results: list,
        top_k: Optional[int] = None,
    ) -> list[RankedResult]:
        """
        Rerank search results using cross-encoder.
        
        Args:
            query: The search query
            results: List of SearchResult objects from vector search
            top_k: Number of results to return (None = all)
            
        Returns:
            List of RankedResult objects sorted by rerank score
        """
        if not results:
            return []
        
        # Create query-document pairs
        pairs = [(query, r.text) for r in results]
        
        # Get cross-encoder scores
        scores = self.model.predict(
            pairs,
            batch_size=self.config.batch_size,
            show_progress_bar=False,
        )
        
        # Normalize scores to 0-1 range
        if self.config.normalize_scores:
            scores = self._normalize_scores(scores)
        
        # Create ranked results
        ranked = []
        for result, score in zip(results, scores):
            ranked.append(RankedResult(
                text=result.text,
                chunk_id=result.chunk_id,
                source_path=result.source_path,
                original_score=result.score,
                rerank_score=float(score),
                chunk_index=result.chunk_index,
                token_count=result.token_count,
                metadata=getattr(result, 'metadata', {}),
            ))
        
        # Sort by rerank score (descending)
        ranked.sort(key=lambda x: x.rerank_score, reverse=True)
        
        if top_k:
            ranked = ranked[:top_k]
        
        return ranked
    
    def _normalize_scores(self, scores: np.ndarray) -> np.ndarray:
        """Normalize scores to 0-1 range using sigmoid."""
        return 1 / (1 + np.exp(-scores))
