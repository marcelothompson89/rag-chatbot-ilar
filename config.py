import os
from dotenv import load_dotenv
import sys
from io import StringIO

# Cargar variables del archivo .env
load_dotenv()

class Config:
    def __init__(self):
        # Detectar si estamos en Streamlit Cloud o desarrollo local
        self.is_streamlit_cloud = self._detect_streamlit_cloud()
        
        if self.is_streamlit_cloud:
            # Streamlit Cloud - usar secrets
            self._load_from_streamlit_secrets()
        else:
            # Desarrollo local - usar .env
            self._load_from_env()
    
    def _detect_streamlit_cloud(self):
        """Detecta si estamos ejecutando en Streamlit Cloud"""
        # Streamlit Cloud tiene estas características
        return (
            os.getenv("STREAMLIT_SHARING_MODE") is not None or
            os.getenv("STREAMLIT_SERVER_HEADLESS") == "true" or
            "streamlit.io" in os.getenv("HOSTNAME", "") or
            "/mount/src" in os.getcwd()
        )
    
    def _load_from_streamlit_secrets(self):
        """Cargar desde Streamlit secrets (Cloud)"""
        try:
            import streamlit as st
            self.OPENAI_API_KEY = st.secrets.get("OPENAI_API_KEY")
            self.PINECONE_API_KEY = st.secrets.get("PINECONE_API_KEY")
            self.DOCUMENTS_FOLDER = st.secrets.get("DOCUMENTS_FOLDER", "documentos")
        except:
            # Fallback a variables de entorno si falla
            self._load_from_env()
    
    def _load_from_env(self):
        """Cargar desde variables de entorno (.env)"""
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
            location = "secrets.toml" if self.is_streamlit_cloud else "archivo .env"
            errors.append(f"OpenAI API Key no configurada en {location}")
        
        if not self.PINECONE_API_KEY or self.PINECONE_API_KEY.startswith('your'):
            location = "secrets.toml" if self.is_streamlit_cloud else "archivo .env"
            errors.append(f"Pinecone API Key no configurada en {location}")
        
        return errors