# from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv

# def get_embeddings() -> OpenAIEmbeddings:
def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    """
    # Returns an instance of OpenAIEmbeddings.
    Returns an instance of GoogleGenerativeAIEmbeddings.
    
    CONCEPT: Embeddings
    An embedding is a numerical vector (a list of numbers) representing the 
    semantic meaning of a piece of text.
    - Similiar meanings are mapped to vectors that are close to each other in vector space.
    - We use text-embedding-3-small as a fast, cost-efficient model.
    """
    load_dotenv()
    # return OpenAIEmbeddings(model="text-embedding-3-small")
    return GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-2")
