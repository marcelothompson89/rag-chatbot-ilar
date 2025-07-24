import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
    DOCUMENTS_FOLDER = os.getenv("DOCUMENTS_FOLDER", "documentos")
    
    # Configuraciones del sistema
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    INDEX_NAME = "documentos-cliente"
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o-mini-2024-07-18"