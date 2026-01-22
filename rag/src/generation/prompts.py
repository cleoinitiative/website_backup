"""Prompt templates for RAG generation."""

from dataclasses import dataclass
from typing import Optional
from string import Template


@dataclass
class PromptTemplate:
    """A prompt template with system and user message templates."""
    
    name: str
    system_template: str
    user_template: str
    description: str = ""
    
    def format_system(self, **kwargs) -> str:
        """Format the system message with provided variables."""
        return Template(self.system_template).safe_substitute(**kwargs)
    
    def format_user(self, **kwargs) -> str:
        """Format the user message with provided variables."""
        return Template(self.user_template).safe_substitute(**kwargs)
    
    def format(
        self,
        query: str,
        context: str,
        **extra_kwargs,
    ) -> tuple[str, str]:
        """
        Format both system and user messages.
        
        Args:
            query: The user's question
            context: Retrieved context chunks
            **extra_kwargs: Additional template variables
            
        Returns:
            Tuple of (system_message, user_message)
        """
        kwargs = {"query": query, "context": context, **extra_kwargs}
        return self.format_system(**kwargs), self.format_user(**kwargs)


# =============================================================================
# Built-in Prompt Templates
# =============================================================================

RAG_PROMPT = PromptTemplate(
    name="rag_default",
    description="Standard RAG prompt for question answering with citations",
    system_template="""You are a helpful assistant that answers questions based on the provided context.

Guidelines:
- Answer based ONLY on the provided context
- If the context doesn't contain enough information, say so
- Cite sources using [Source: filename] format
- Be concise but complete
- If multiple sources agree, synthesize them
- If sources conflict, acknowledge the discrepancy""",
    
    user_template="""Context:
$context

---

Question: $query

Please answer the question based on the context above. Include citations to the source documents.""",
)


QA_PROMPT = PromptTemplate(
    name="qa_strict",
    description="Strict Q&A prompt that refuses to answer without evidence",
    system_template="""You are a precise question-answering system. You must:
1. ONLY answer using information explicitly stated in the provided context
2. Quote relevant passages when possible
3. If the answer is not in the context, respond with "I cannot answer this based on the provided documents."
4. Never make assumptions or use external knowledge""",
    
    user_template="""Documents:
$context

---

Question: $query

Provide a precise answer using only the documents above.""",
)


SUMMARY_PROMPT = PromptTemplate(
    name="summary",
    description="Summarization prompt for condensing retrieved content",
    system_template="""You are a summarization assistant. Create clear, concise summaries that:
- Capture the main points and key information
- Maintain factual accuracy
- Organize information logically
- Note any conflicting information across sources""",
    
    user_template="""Content to summarize:
$context

---

$query

Provide a comprehensive summary of the above content.""",
)


CONVERSATIONAL_PROMPT = PromptTemplate(
    name="conversational",
    description="Conversational RAG with chat history support",
    system_template="""You are a helpful conversational assistant with access to a knowledge base.

Guidelines:
- Answer questions using the provided context
- Maintain a natural, conversational tone
- Reference previous conversation when relevant
- If you don't know something, say so honestly
- Suggest follow-up questions when appropriate""",
    
    user_template="""$chat_history

Context from knowledge base:
$context

---

User: $query

Please respond helpfully based on the context and our conversation.""",
)


# Registry of built-in prompts
PROMPT_REGISTRY = {
    "rag": RAG_PROMPT,
    "qa": QA_PROMPT,
    "summary": SUMMARY_PROMPT,
    "conversational": CONVERSATIONAL_PROMPT,
}


def get_prompt(name: str) -> PromptTemplate:
    """Get a prompt template by name."""
    if name not in PROMPT_REGISTRY:
        available = ", ".join(PROMPT_REGISTRY.keys())
        raise ValueError(f"Unknown prompt: {name}. Available: {available}")
    return PROMPT_REGISTRY[name]
