"""Advanced retrieval strategies including MMR and parent-child retrieval."""

from dataclasses import dataclass, field
from typing import Optional, Literal, Any
import asyncio
import logging

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class RetrievalConfig:
    """Configuration for advanced retrieval."""
    
    # Initial retrieval
    initial_k: int = 20  # Candidates for reranking/MMR
    final_k: int = 5     # Final results to return
    
    # MMR settings
    use_mmr: bool = True
    mmr_lambda: float = 0.7  # Balance relevance (1.0) vs diversity (0.0)
    
    # Reranking
    use_reranking: bool = True
    rerank_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    rerank_device: str = "cpu"
    
    # Parent-child retrieval
    use_parent_child: bool = False
    parent_chunk_size: int = 2048  # Larger context window
    child_chunk_size: int = 256   # Smaller for precise matching
    
    # Score thresholds
    min_score: Optional[float] = None  # Filter low-relevance results


@dataclass 
class RetrievalResult:
    """A retrieved chunk with all scores and metadata."""
    
    text: str
    chunk_id: str
    source_path: str
    
    # Scores
    vector_score: float      # Bi-encoder similarity
    rerank_score: float      # Cross-encoder relevance (if reranked)
    mmr_score: float         # MMR-adjusted score (if MMR applied)
    final_score: float       # Final ranking score
    
    # Metadata
    chunk_index: int = 0
    token_count: int = 0
    start_char: int = 0
    end_char: int = 0
    
    # Parent context (if parent-child retrieval)
    parent_text: Optional[str] = None
    
    metadata: dict = field(default_factory=dict)


def mmr_rerank(
    query_embedding: np.ndarray,
    candidate_embeddings: np.ndarray,
    candidate_scores: np.ndarray,
    k: int,
    lambda_param: float = 0.7,
) -> list[int]:
    """
    Maximal Marginal Relevance reranking for diversity.
    
    MMR balances relevance to query with diversity among selected results:
    MMR = argmax[λ * sim(doc, query) - (1-λ) * max(sim(doc, selected))]
    
    Args:
        query_embedding: Query vector (D,)
        candidate_embeddings: Document vectors (N, D)
        candidate_scores: Original relevance scores (N,)
        k: Number of results to select
        lambda_param: Trade-off parameter (1=relevance only, 0=diversity only)
        
    Returns:
        List of selected indices in MMR order
    """
    if len(candidate_embeddings) == 0:
        return []
    
    k = min(k, len(candidate_embeddings))
    
    # Normalize embeddings for cosine similarity
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
    doc_norms = candidate_embeddings / (
        np.linalg.norm(candidate_embeddings, axis=1, keepdims=True) + 1e-10
    )
    
    # Compute query-document similarities
    query_sims = doc_norms @ query_norm
    
    # Precompute document-document similarities
    doc_sims = doc_norms @ doc_norms.T
    
    selected_indices: list[int] = []
    remaining_indices = list(range(len(candidate_embeddings)))
    
    for _ in range(k):
        if not remaining_indices:
            break
        
        mmr_scores = []
        
        for idx in remaining_indices:
            # Relevance to query (use original scores or embedding similarity)
            relevance = float(candidate_scores[idx])
            
            # Maximum similarity to already selected documents
            if selected_indices:
                max_sim_to_selected = max(
                    doc_sims[idx, sel_idx] for sel_idx in selected_indices
                )
            else:
                max_sim_to_selected = 0.0
            
            # MMR score
            mmr = lambda_param * relevance - (1 - lambda_param) * max_sim_to_selected
            mmr_scores.append((idx, mmr))
        
        # Select document with highest MMR score
        best_idx = max(mmr_scores, key=lambda x: x[1])[0]
        selected_indices.append(best_idx)
        remaining_indices.remove(best_idx)
    
    return selected_indices


class Retriever:
    """
    Advanced retriever combining multiple strategies.
    
    Pipeline:
    1. Initial vector search (bi-encoder)
    2. Optional reranking (cross-encoder)
    3. Optional MMR for diversity
    4. Optional parent context expansion
    """
    
    def __init__(
        self,
        embedder,  # Embedder instance
        vector_store,  # VectorStore instance  
        config: Optional[RetrievalConfig] = None,
    ):
        self.embedder = embedder
        self.vector_store = vector_store
        self.config = config or RetrievalConfig()
        self._reranker = None
    
    @property
    def reranker(self):
        """Lazy-load reranker if needed."""
        if self._reranker is None and self.config.use_reranking:
            from ..reranking import Reranker, RerankerConfig
            self._reranker = Reranker(RerankerConfig(
                model_name=self.config.rerank_model,
                device=self.config.rerank_device,
            ))
        return self._reranker
    
    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter_expr: Optional[str] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks with advanced strategies.
        
        Args:
            query: Search query
            k: Number of final results (overrides config.final_k)
            filter_expr: Optional filter expression
            
        Returns:
            List of RetrievalResult objects
        """
        final_k = k or self.config.final_k
        
        # Step 1: Initial vector search
        query_embedding = self.embedder.embed_query(query)
        initial_results = self.vector_store.search(
            query_embedding,
            limit=self.config.initial_k,
            filter_expr=filter_expr,
        )
        
        if not initial_results:
            return []
        
        # Convert to internal format with embeddings
        candidates = self._prepare_candidates(initial_results, query_embedding)
        
        # Step 2: Optional reranking
        if self.config.use_reranking and self.reranker:
            candidates = self._apply_reranking(query, candidates)
        
        # Step 3: Optional MMR for diversity
        if self.config.use_mmr:
            candidates = self._apply_mmr(query_embedding, candidates, final_k)
        else:
            # Just take top-k by current score
            candidates = sorted(
                candidates, 
                key=lambda x: x['score'], 
                reverse=True
            )[:final_k]
        
        # Step 4: Apply score threshold if configured
        if self.config.min_score is not None:
            candidates = [c for c in candidates if c['score'] >= self.config.min_score]
        
        # Convert to RetrievalResult objects
        return self._build_results(candidates)
    
    def _prepare_candidates(
        self,
        results: list,
        query_embedding: np.ndarray,
    ) -> list[dict]:
        """Prepare candidate documents with embeddings."""
        candidates = []
        
        for result in results:
            # Get embedding from vector store if available
            embedding = self._get_embedding(result.chunk_id)
            
            candidates.append({
                'text': result.text,
                'chunk_id': result.chunk_id,
                'source_path': result.source_path,
                'chunk_index': result.chunk_index,
                'token_count': result.token_count,
                'vector_score': result.score,
                'rerank_score': result.score,  # Default to vector score
                'score': result.score,
                'embedding': embedding,
                'metadata': getattr(result, 'metadata', {}),
            })
        
        return candidates
    
    def _get_embedding(self, chunk_id: str) -> Optional[np.ndarray]:
        """Retrieve stored embedding for a chunk."""
        try:
            if self.vector_store.table is None:
                return None
            
            df = self.vector_store.table.search().where(
                f"chunk_id = '{chunk_id}'"
            ).limit(1).to_pandas()
            
            if len(df) > 0 and 'embedding' in df.columns:
                return np.array(df.iloc[0]['embedding'])
        except Exception as e:
            logger.debug(f"Could not retrieve embedding for {chunk_id}: {e}")
        
        return None
    
    def _apply_reranking(self, query: str, candidates: list[dict]) -> list[dict]:
        """Apply cross-encoder reranking."""
        # Create pseudo SearchResult objects for reranker
        from ..storage import SearchResult
        search_results = [
            SearchResult(
                text=c['text'],
                chunk_id=c['chunk_id'],
                source_path=c['source_path'],
                score=c['vector_score'],
                chunk_index=c['chunk_index'],
                token_count=c['token_count'],
            )
            for c in candidates
        ]
        
        # Rerank
        reranked = self.reranker.rerank(query, search_results)
        
        # Update candidates with rerank scores
        rerank_map = {r.chunk_id: r.rerank_score for r in reranked}
        
        for candidate in candidates:
            if candidate['chunk_id'] in rerank_map:
                candidate['rerank_score'] = rerank_map[candidate['chunk_id']]
                candidate['score'] = candidate['rerank_score']
        
        return candidates
    
    def _apply_mmr(
        self,
        query_embedding: np.ndarray,
        candidates: list[dict],
        k: int,
    ) -> list[dict]:
        """Apply MMR reranking for diversity."""
        # Get embeddings for candidates
        embeddings = []
        valid_candidates = []
        
        for c in candidates:
            if c['embedding'] is not None:
                embeddings.append(c['embedding'])
                valid_candidates.append(c)
            else:
                # Re-embed if no stored embedding
                emb = self.embedder.embed_texts([c['text']])[0]
                embeddings.append(emb)
                valid_candidates.append(c)
        
        if not embeddings:
            return candidates[:k]
        
        embeddings = np.array(embeddings)
        scores = np.array([c['score'] for c in valid_candidates])
        
        # Apply MMR
        selected_indices = mmr_rerank(
            query_embedding=np.array(query_embedding),
            candidate_embeddings=embeddings,
            candidate_scores=scores,
            k=k,
            lambda_param=self.config.mmr_lambda,
        )
        
        # Reorder candidates and add MMR scores
        result = []
        for rank, idx in enumerate(selected_indices):
            candidate = valid_candidates[idx].copy()
            # MMR score decreases by rank
            candidate['mmr_score'] = 1.0 - (rank / max(len(selected_indices), 1))
            result.append(candidate)
        
        return result
    
    def _build_results(self, candidates: list[dict]) -> list[RetrievalResult]:
        """Convert candidate dicts to RetrievalResult objects."""
        results = []
        
        for c in candidates:
            results.append(RetrievalResult(
                text=c['text'],
                chunk_id=c['chunk_id'],
                source_path=c['source_path'],
                vector_score=c['vector_score'],
                rerank_score=c.get('rerank_score', c['vector_score']),
                mmr_score=c.get('mmr_score', 1.0),
                final_score=c['score'],
                chunk_index=c['chunk_index'],
                token_count=c['token_count'],
                metadata=c.get('metadata', {}),
            ))
        
        return results
    
    async def retrieve_async(
        self,
        query: str,
        k: Optional[int] = None,
        filter_expr: Optional[str] = None,
    ) -> list[RetrievalResult]:
        """
        Retrieve relevant chunks asynchronously.
        
        Runs CPU-bound operations (embedding, reranking) in a thread pool
        to avoid blocking the event loop.
        
        Args:
            query: Search query
            k: Number of final results (overrides config.final_k)
            filter_expr: Optional filter expression
            
        Returns:
            List of RetrievalResult objects
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            lambda: self.retrieve(query, k=k, filter_expr=filter_expr)
        )


