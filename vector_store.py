# vector_store.py (Versión Simplificada)
from pinecone import Pinecone, ServerlessSpec
from typing import List
from langchain.schema import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from config import Config
import time

class VectorStoreManager:
    def __init__(self):
        self.config = Config()
        self.embeddings = OpenAIEmbeddings(
            model=self.config.EMBEDDING_MODEL,
            api_key=self.config.OPENAI_API_KEY
        )
        self.init_pinecone()
    
    def init_pinecone(self):
        """Inicializa conexión con Pinecone (nueva versión)"""
        print("🔄 Conectando con Pinecone...")
        
        # Inicializar cliente de Pinecone
        self.pc = Pinecone(api_key=self.config.PINECONE_API_KEY)
        
        # Verificar si el índice existe
        existing_indexes = [index.name for index in self.pc.list_indexes()]
        
        if self.config.INDEX_NAME not in existing_indexes:
            print(f"📝 Creando índice '{self.config.INDEX_NAME}'...")
            
            # Crear índice con configuración serverless (gratis)
            self.pc.create_index(
                name=self.config.INDEX_NAME,
                dimension=1536,  # Dimensión para text-embedding-3-small
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            
            # Esperar a que esté listo
            print("⏳ Esperando a que el índice esté listo...")
            time.sleep(10)
            print(f"✅ Índice '{self.config.INDEX_NAME}' creado")
        else:
            print(f"✅ Índice '{self.config.INDEX_NAME}' ya existe")
        
        # Conectar al índice
        self.index = self.pc.Index(self.config.INDEX_NAME)
    
    def store_documents(self, documents: List[Document]) -> bool:
        """Almacena documentos en la base vectorial"""
        if not documents:
            print("❌ No hay documentos para almacenar")
            return False
        
        try:
            print(f"🔄 Almacenando {len(documents)} documentos en Pinecone...")
            
            # Crear vector store desde documentos
            vector_store = PineconeVectorStore.from_documents(
                documents=documents,
                embedding=self.embeddings,
                index_name=self.config.INDEX_NAME
            )
            
            print(f"✅ {len(documents)} documentos almacenados correctamente")
            return True
        
        except Exception as e:
            print(f"❌ Error almacenando documentos: {e}")
            return False
    
    def get_vector_store(self):
        """Retorna el vector store para búsquedas"""
        return PineconeVectorStore(
            index_name=self.config.INDEX_NAME,
            embedding=self.embeddings
        )
    
    def search_similar_documents(self, query: str, k: int = 4) -> List[Document]:
        """Busca documentos similares a la consulta"""
        try:
            vector_store = self.get_vector_store()
            results = vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"❌ Error en búsqueda: {e}")
            return []
    
    def get_index_stats(self) -> dict:
        """Obtiene estadísticas del índice"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get("total_vector_count", 0),
                "dimension": stats.get("dimension", 0),
                "namespaces": stats.get("namespaces", {})
            }
        except Exception as e:
            print(f"❌ Error obteniendo estadísticas: {e}")
            return {"error": str(e)}
    
    def clear_index(self):
        """Limpia todos los vectores del índice"""
        try:
            self.index.delete(delete_all=True)
            print("✅ Índice limpiado")
            return True
        except Exception as e:
            print(f"❌ Error limpiando índice: {e}")
            return False
    
    def delete_index(self):
        """Elimina el índice completamente"""
        try:
            self.pc.delete_index(self.config.INDEX_NAME)
            print(f"✅ Índice '{self.config.INDEX_NAME}' eliminado")
            return True
        except Exception as e:
            print(f"❌ Error eliminando índice: {e}")
            return False