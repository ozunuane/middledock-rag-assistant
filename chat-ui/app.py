"""
MiddleDock Chat UI — Gradio interface for employees to ask policy questions
and upload new documents to the knowledge base.

Usage: python app.py
Opens at http://localhost:7860
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vector-db"))

import gradio as gr
from agent.rag import MiddleDockAgent
from ingest import ingest_single_file

agent = MiddleDockAgent()


def chat_fn(message, history):
    """Handle a chat message using the RAG agent."""
    return agent.ask(message)


def upload_document(file) -> str:
    """Upload a new document to the knowledge base."""
    if file is None:
        return "No file selected."
    try:
        with open(file, "r") as f:
            content = f.read()
        filename = os.path.basename(file)
        count = ingest_single_file(file, content=content)
        return f"Ingested '{filename}' — {count} chunks added to the knowledge base. You can now ask questions about it."
    except Exception as e:
        return f"Error ingesting file: {str(e)}"


with gr.Blocks(title="MiddleDock Policy Assistant") as demo:
    gr.Markdown("# MiddleDock Policy Assistant")
    gr.Markdown("Ask questions about company policies or upload new documents to the knowledge base.")

    with gr.Tabs():
        with gr.Tab("Chat"):
            gr.ChatInterface(
                fn=chat_fn,
                examples=[
                    "How many PTO days do I get per year?",
                    "What's the maximum hotel rate for NYC?",
                    "Can I work remotely from another country?",
                    "What's the password policy?",
                    "How do I report a security incident?",
                    "What's the parental leave policy?",
                    "Can I expense a conference ticket?",
                    "What happens on Focus Fridays?",
                ],
            )

        with gr.Tab("Upload Document"):
            gr.Markdown("""
            ### Add a new policy document to the knowledge base

            Upload a `.md` or `.txt` file. The document will be chunked, embedded,
            and added to the vector database. You can immediately ask questions about it
            in the Chat tab.
            """)
            file_input = gr.File(label="Upload policy document", file_types=[".md", ".txt"])
            upload_btn = gr.Button("Ingest Document", variant="primary")
            upload_output = gr.Textbox(label="Result", interactive=False)
            upload_btn.click(fn=upload_document, inputs=file_input, outputs=upload_output)

        with gr.Tab("About"):
            gr.Markdown("""
            ### How it works

            1. Your question is embedded into a vector
            2. Qdrant finds the most relevant policy chunks
            3. The chunks + your question are sent to the LLM
            4. The LLM answers using only the provided context

            **LLM:** Qwen2.5-7B-Instruct (AWQ) on vLLM
            **Vector DB:** Qdrant with sentence-transformers
            **Contact:** hr@middledock.com for questions not in our policies
            """)

if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
