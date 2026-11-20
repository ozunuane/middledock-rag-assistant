"""
MiddleDock RAG Agent — retrieves policy context from Qdrant, queries vLLM/SGLang.

This is the core logic used by both the chat UI and batch processor.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

load_dotenv()

LLM_BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:8000/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "tok_bench2026")
LLM_MODEL = os.getenv("LLM_MODEL", "Qwen/Qwen2.5-7B-Instruct")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
COLLECTION_NAME = "middledock_policies"

SYSTEM_PROMPT = """You are MiddleDock's internal policy assistant. You help employees find answers about company policies, rules, and standards.

Rules:
- Answer ONLY based on the provided context. Do not make up information.
- If the context doesn't contain the answer, say "I couldn't find that in our policies. Please contact HR at hr@middledock.com."
- Quote the specific policy name and section when possible.
- Keep answers concise and direct.
- If the question is ambiguous, ask for clarification."""


class MiddleDockAgent:
    def __init__(self):
        self.llm = OpenAI(base_url=LLM_BASE_URL, api_key=LLM_API_KEY)
        self.qdrant = QdrantClient(url=QDRANT_URL)
        self.embedder = SentenceTransformer(EMBEDDING_MODEL)

    def retrieve_context(self, query: str, top_k: int = 5) -> str:
        """Search Qdrant for relevant policy chunks."""
        query_embedding = self.embedder.encode(query).tolist()

        results = self.qdrant.query_points(
            collection_name=COLLECTION_NAME,
            query=query_embedding,
            limit=top_k,
        ).points

        if not results:
            return "No relevant policies found."

        context_parts = []
        for result in results:
            source = result.payload.get("source", "unknown")
            section = result.payload.get("section", "")
            text = result.payload.get("text", "")
            context_parts.append(f"[{source} > {section}]\n{text}")

        return "\n\n---\n\n".join(context_parts)

    def ask(self, question: str, stream: bool = False) -> str:
        """RAG pipeline: retrieve context → build prompt → query LLM."""
        context = self.retrieve_context(question)

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": f"Context from MiddleDock policies:\n\n{context}\n\n---\n\nEmployee question: {question}",
            },
        ]

        if stream:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
                stream=True,
            )
            return response  # caller iterates over chunks
        else:
            response = self.llm.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=500,
                temperature=0.3,
            )
            return response.choices[0].message.content
