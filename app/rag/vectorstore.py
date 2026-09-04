import os
from langchain_chroma import Chroma
from app.rag.embeddings import get_embeddings

# Save the database folder in data/chroma_db
CHROMA_PATH = "data/chroma_db"

def get_vectorstore() -> Chroma:
    """
    Initializes and returns the Chroma vector database.
    
    CONCEPT: Vector Store (Vector DB)
    A Vector Database indexes text chunks alongside their semantic vectors.
    This lets us perform "Similarity Search" (nearest neighbor searches)
    to find chunks of text that match the meaning of the user's query.
    """
    os.makedirs("data", exist_ok=True)
    embeddings = get_embeddings()
    return Chroma(
        persist_directory=CHROMA_PATH,
        embedding_function=embeddings
    )

def add_documents_to_store(documents):
    """
    Adds split document chunks to the vector database.
    """
    vectorstore = get_vectorstore()
    vectorstore.add_documents(documents)
