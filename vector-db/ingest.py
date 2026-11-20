"""
Ingest MiddleDock policy documents into Qdrant vector database.
Run once to load docs, then the agent queries at request time.

Usage: python ingest.py --docs-dir ../docs/policies
"""

import os
import glob
import argparse
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()

COLLECTION_NAME = "middledock_policies"
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")


def load_documents(docs_dir: str) -> list[dict]:
    """Load all markdown files and split into chunks."""
    docs = []
    for filepath in glob.glob(os.path.join(docs_dir, "*.md")):
        filename = os.path.basename(filepath)
        with open(filepath, "r") as f:
            content = f.read()

        # Split by markdown headers first
        header_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "title"), ("##", "section"), ("###", "subsection")]
        )
        header_chunks = header_splitter.split_text(content)

        # Then split long sections into smaller chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
        )

        for chunk in header_chunks:
            sub_chunks = text_splitter.split_text(chunk.page_content)
            for sub in sub_chunks:
                metadata = {**chunk.metadata, "source": filename}
                docs.append({"text": sub, "metadata": metadata})

    return docs


def get_client_and_model():
    """Return Qdrant client and embedding model, ensuring collection exists."""
    model = SentenceTransformer(EMBEDDING_MODEL)
    dimension = model.get_sentence_embedding_dimension()
    client = QdrantClient(url=QDRANT_URL)

    # Create collection if it doesn't exist
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    return client, model


def get_next_id(client: QdrantClient) -> int:
    """Get the next available point ID."""
    info = client.get_collection(COLLECTION_NAME)
    return info.points_count


def ingest_directory(docs_dir: str, recreate: bool = True):
    """Ingest all markdown files from a directory."""
    print(f"Loading documents from {docs_dir}")
    documents = load_documents(docs_dir)
    print(f"Loaded {len(documents)} chunks from {len(glob.glob(os.path.join(docs_dir, '*.md')))} files")

    print(f"Loading embedding model: {EMBEDDING_MODEL}")
    model = SentenceTransformer(EMBEDDING_MODEL)
    dimension = model.get_sentence_embedding_dimension()

    print(f"Connecting to Qdrant at {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL)

    if recreate:
        client.recreate_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )

    # Embed and upload
    texts = [doc["text"] for doc in documents]
    print(f"Embedding {len(texts)} chunks...")
    embeddings = model.encode(texts, show_progress_bar=True)

    start_id = 0 if recreate else get_next_id(client)
    points = [
        PointStruct(
            id=start_id + i,
            vector=embedding.tolist(),
            payload={"text": doc["text"], **doc["metadata"]},
        )
        for i, (doc, embedding) in enumerate(zip(documents, embeddings))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Ingested {len(points)} chunks into collection '{COLLECTION_NAME}'")
    return len(points)


def ingest_single_file(filepath: str, content: str = None) -> int:
    """Ingest a single file into the existing collection (append, not replace).

    Args:
        filepath: path to the file, or just a filename if content is provided
        content: file content as string (if None, reads from filepath)

    Returns:
        Number of chunks ingested
    """
    client, model = get_client_and_model()

    if content is None:
        with open(filepath, "r") as f:
            content = f.read()

    filename = os.path.basename(filepath)

    # Chunk the document
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("#", "title"), ("##", "section"), ("###", "subsection")]
    )
    header_chunks = header_splitter.split_text(content)

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
    )

    documents = []
    for chunk in header_chunks:
        sub_chunks = text_splitter.split_text(chunk.page_content)
        for sub in sub_chunks:
            metadata = {**chunk.metadata, "source": filename}
            documents.append({"text": sub, "metadata": metadata})

    if not documents:
        # Plain text without headers — split directly
        sub_chunks = text_splitter.split_text(content)
        for sub in sub_chunks:
            documents.append({"text": sub, "metadata": {"source": filename}})

    # Embed
    texts = [doc["text"] for doc in documents]
    embeddings = model.encode(texts)

    # Append to collection
    start_id = get_next_id(client)
    points = [
        PointStruct(
            id=start_id + i,
            vector=embedding.tolist(),
            payload={"text": doc["text"], **doc["metadata"]},
        )
        for i, (doc, embedding) in enumerate(zip(documents, embeddings))
    ]

    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--docs-dir", default="../docs/policies")
    parser.add_argument("--file", help="Ingest a single file (appends to existing collection)")
    args = parser.parse_args()

    if args.file:
        count = ingest_single_file(args.file)
        print(f"Ingested {count} chunks from {args.file}")
    else:
        ingest_directory(args.docs_dir)
