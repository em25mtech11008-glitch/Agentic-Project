from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(documents, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Splits long documents into smaller chunks.
    
    CONCEPT: Text Splitting
    Why split text?
    1. LLMs have a context window limit (token limit).
    2. We only want to retrieve the RELEVANT section to answer a question, not 
       the entire 100-page document (which would be costly and introduce noise).
    
    RecursiveCharacterTextSplitter splits by a list of characters in order:
    ["\n\n", "\n", " ", ""]. It tries to keep paragraphs, sentences, and words 
    intact while keeping the chunks around the desired size.
    
    chunk_overlap preserves semantic context between adjacent chunks.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True # Adds starting character index in metadata
    )
    return splitter.split_documents(documents)
