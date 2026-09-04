from langchain_community.document_loaders import PyPDFLoader

def load_pdf(file_path: str):
    """
    Loads and parses a PDF document from the given file path.
    
    CONCEPT: Document Loader
    A Document Loader takes a raw source (like a PDF, Web Page, CSV, etc.)
    and parses it into a list of LangChain Document objects.
    Each Document contains:
    - page_content: The actual parsed text.
    - metadata: A dictionary with metadata (e.g. source file name, page number).
    """
    loader = PyPDFLoader(file_path)
    return loader.load()
