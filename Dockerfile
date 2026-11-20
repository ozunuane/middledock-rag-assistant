FROM python:3.12-slim

WORKDIR /app

# Install in stages to avoid timeout on large packages
RUN pip install --no-cache-dir --timeout=120 torch --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir --timeout=120 sentence-transformers
RUN pip install --no-cache-dir --timeout=120 openai qdrant-client gradio langchain-text-splitters python-dotenv

COPY agent/ agent/
COPY vector-db/ vector-db/
COPY chat-ui/ chat-ui/
COPY docs/ docs/

EXPOSE 7860

CMD ["python", "chat-ui/app.py"]
