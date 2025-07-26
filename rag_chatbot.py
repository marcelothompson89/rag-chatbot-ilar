# rag_chatbot.py (Versión Simplificada)
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from vector_store import VectorStoreManager
from config import Config

class RAGChatbot:
    def __init__(self):
        self.config = Config()
        self.vector_manager = VectorStoreManager()
        self.llm = ChatOpenAI(
            model=self.config.CHAT_MODEL,
            temperature=0.1,
            api_key=self.config.OPENAI_API_KEY
        )
        
        # Template mejorado para el prompt
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""
Eres un asistente experto que responde preguntas basándose únicamente en los documentos proporcionados.

CONTEXTO DE LOS DOCUMENTOS:
{context}

PREGUNTA DEL USUARIO: {question}

INSTRUCCIONES IMPORTANTES:
1. Responde ÚNICAMENTE basándote en la información del contexto proporcionado
2. Si la información no está en el contexto, indica claramente: "No encuentro esa información en los documentos proporcionados"
3. Sé preciso, claro y conciso
4. Responde siempre en español
5. Si hay múltiples respuestas posibles, menciona todas las relevantes

RESPUESTA:"""
        )
        
        self.qa_chain = None
    
    def setup_retrieval_chain(self):
        """Configura la cadena de recuperación y generación"""
        print("🔄 Configurando cadena RAG...")
        
        try:
            vector_store = self.vector_manager.get_vector_store()
            
            self.qa_chain = RetrievalQA.from_chain_type(
                llm=self.llm,
                chain_type="stuff",
                retriever=vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}  # Número de chunks relevantes
                ),
                chain_type_kwargs={"prompt": self.prompt_template},
                return_source_documents=True
            )
            
            print("✅ Cadena RAG configurada correctamente")
            return True
            
        except Exception as e:
            print(f"❌ Error configurando RAG: {e}")
            return False
    
    def chat(self, question: str) -> Dict:
        """Procesa una pregunta y retorna respuesta con fuentes"""
        if not self.qa_chain:
            return {
                "answer": "❌ El sistema no está configurado. Ejecuta setup_retrieval_chain() primero.",
                "sources": [],
                "success": False
            }
        
        if not question.strip():
            return {
                "answer": "Por favor, haz una pregunta específica sobre tus documentos.",
                "sources": [],
                "success": True
            }
        
        try:
            print(f"🔍 Procesando pregunta: {question[:50]}...")
            
            # Ejecutar la cadena RAG
            result = self.qa_chain.invoke({"query": question})
            
            # Extraer fuentes únicas
            sources = self._extract_sources(result.get("source_documents", []))
            
            print(f"✅ Respuesta generada con {len(sources)} fuentes")
            
            return {
                "answer": result["result"],
                "sources": sources,
                "success": True
            }
        
        except Exception as e:
            print(f"❌ Error procesando consulta: {e}")
            return {
                "answer": f"❌ Error procesando la consulta: {str(e)}",
                "sources": [],
                "success": False
            }
    
    def _extract_sources(self, source_documents) -> List[Dict]:
        """Extrae información de las fuentes de manera única"""
        sources = []
        seen_sources = set()
        
        for doc in source_documents:
            source_info = {
                "filename": doc.metadata.get("source", "Documento desconocido"),
                "chunk_id": doc.metadata.get("chunk_id", 0),
                "preview": doc.page_content[:150] + "..." if len(doc.page_content) > 150 else doc.page_content
            }
            
            # Crear clave única para evitar duplicados
            source_key = f"{source_info['filename']}-{source_info['chunk_id']}"
            
            if source_key not in seen_sources:
                sources.append(source_info)
                seen_sources.add(source_key)
        
        return sources
    
    def get_system_stats(self) -> Dict:
        """Obtiene estadísticas del sistema"""
        try:
            vector_stats = self.vector_manager.get_index_stats()
            
            return {
                "total_documents": vector_stats.get("total_vectors", 0),
                "vector_dimension": vector_stats.get("dimension", 0),
                "model_used": self.config.CHAT_MODEL,
                "embedding_model": self.config.EMBEDDING_MODEL,
                "status": "✅ Sistema operativo" if self.qa_chain else "⚠️ Sistema no configurado"
            }
            
        except Exception as e:
            return {
                "status": f"❌ Error: {str(e)}",
                "error": True
            }
    
    def test_system(self) -> bool:
        """Realiza una prueba rápida del sistema"""
        print("🧪 Realizando prueba del sistema...")
        
        try:
            # Configurar si no está configurado
            if not self.qa_chain:
                if not self.setup_retrieval_chain():
                    return False
            
            # Pregunta de prueba
            test_question = "¿Qué temas o información principal contienen estos documentos?"
            result = self.chat(test_question)
            
            if result["success"] and result["sources"]:
                print("✅ Prueba del sistema exitosa")
                print(f"📄 Fuentes encontradas: {len(result['sources'])}")
                return True
            else:
                print("⚠️ Prueba completada pero sin fuentes encontradas")
                return False
                
        except Exception as e:
            print(f"❌ Error en prueba del sistema: {e}")
            return False