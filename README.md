# MiddleDock Policy Assistant

Internal AI assistant for MiddleDock employees to query company policies, rules, and standards.

## Architecture

```
Employee → Chat UI (Gradio) → RAG Agent → Vector DB (Qdrant)
                                   ↓
                              vLLM / SGLang (GPU)
```

- **Chat UI**: Gradio web interface for interactive questions
- **Batch**: CSV processor for bulk policy queries
- **Agent**: RAG pipeline — retrieves relevant policy chunks, sends to LLM with context
- **Vector DB**: Qdrant stores embedded policy documents
- **LLM**: vLLM or SGLang serving Qwen2.5-7B-Instruct (OpenAI-compatible API)

## Quick Start

```bash
# 1. Start Qdrant
docker compose up -d

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure
cp .env.example .env
# Edit .env with your vLLM endpoint URL

# 4. Ingest policy documents into Qdrant
python vector-db/ingest.py --docs-dir docs/policies

# 5. Run chat UI
cd chat-ui && python app.py
# Opens at http://localhost:7860

# 6. Or run batch processor
cd batch && python process.py --input questions.csv --output answers.csv
```

## Company Policies

- Remote Work Policy
- Expense & Reimbursement Policy
- Leave & Time-Off Policy
- Information Security Policy
- Code of Conduct

## Engine Routing (Production)

- **Chat UI / Agent workloads** → SGLang (RadixAttention, better prefix caching for multi-turn)
- **Batch processing** → vLLM (PagedAttention, efficient for independent requests)
- Both expose the same OpenAI-compatible API — routing is just a URL change
