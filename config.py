import os
import streamlit as st
from dotenv import load_dotenv

# Cargar variables del archivo .env (para desarrollo local)
load_dotenv()

class Config:
    def __init__(self):
        # En Streamlit Cloud, las variables están en st.secrets
        # En desarrollo local, están en variables de entorno
        if hasattr(st, 'secrets'):
            # Streamlit Cloud
            self.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
            self.PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY", os.getenv("PINECONE_API_KEY"))
            self.DOCUMENTS_FOLDER = st.secrets.get("DOCUMENTS_FOLDER", os.getenv("DOCUMENTS_FOLDER", "documentos"))
        else:
            # Desarrollo local
            self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
            self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
            self.DOCUMENTS_FOLDER = os.getenv("DOCUMENTS_FOLDER", "documentos")
    
    # Configuraciones del sistema
    CHUNK_SIZE = 1000
    CHUNK_OVERLAP = 200
    INDEX_NAME = "documentos-cliente"
    EMBEDDING_MODEL = "text-embedding-3-small"
    CHAT_MODEL = "gpt-4o-mini-2024-07-18"
    
    def validate_keys(self):
        """Valida que las API keys estén configuradas"""
        errors = []
        
        if not self.OPENAI_API_KEY or self.OPENAI_API_KEY.startswith('sk-your'):
            errors.append("OpenAI API Key no configurada")
        
        if not self.PINECONE_API_KEY or self.PINECONE_API_KEY.startswith('your'):
            errors.append("Pinecone API Key no configurada")
        
        return errors