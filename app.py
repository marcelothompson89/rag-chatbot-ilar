# app.py - Interfaz Streamlit simplificada (solo chat)
import streamlit as st
import os
from config import Config
import time
import warnings

warnings.filterwarnings("ignore", message="No secrets files found")

# Configuración de la página
st.set_page_config(
    page_title="🤖 RAG Chatbot - Documentos PDF",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"  # Sidebar colapsado por defecto
)

# CSS personalizado para mejor apariencia
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
        background-color: #f0f2f6;
    }
    .source-box {
        background-color: #e8f4fd;
        padding: 0.5rem;
        border-radius: 0.3rem;
        margin: 0.2rem 0;
        border-left: 3px solid #1f77b4;
    }
    .success-box {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #c3e6cb;
    }
    .error-box {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #f5c6cb;
    }
</style>
""", unsafe_allow_html=True)

def check_configuration():
    """Verifica que la configuración esté correcta"""
    try:
        config = Config()
        errors = config.validate_keys()
        
        if errors:
            st.markdown('<h1 class="main-header">⚙️ Configuración Requerida</h1>', unsafe_allow_html=True)
            st.markdown(f'<div class="error-box"><strong>❌ Configuración Incompleta</strong><br>{"<br>".join(errors)}</div>', unsafe_allow_html=True)
            
            st.markdown("""
            ### 🔧 Configuración requerida:
            
            Para usar este chatbot, necesitas configurar las API keys en el archivo `.env`:
            
            ```
            OPENAI_API_KEY=tu-api-key-de-openai
            PINECONE_API_KEY=tu-api-key-de-pinecone
            ```
            
            1. **OpenAI API Key** - para el modelo de chat
            2. **Pinecone API Key** - para la base de datos vectorial
            
            Después de configurar, recarga la página.
            """)
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Error verificando configuración: {e}")
        st.markdown("""
        ### 💡 Solución:
        
        Asegúrate de tener un archivo `.env` en la raíz del proyecto con:
        
        ```
        OPENAI_API_KEY=tu-api-key-real
        PINECONE_API_KEY=tu-api-key-real
        DOCUMENTS_FOLDER=documentos
        ```
        """)
        return False

def check_system_ready():
    """Verifica si el sistema está listo para usar"""
    try:
        from vector_store import VectorStoreManager
        vector_manager = VectorStoreManager()
        stats = vector_manager.get_index_stats()
        
        if stats.get('total_vectors', 0) > 0:
            return True, stats.get('total_vectors', 0)
        else:
            return False, 0
    except Exception as e:
        return False, 0

def initialize_chatbot():
    """Inicializa el chatbot si no está inicializado"""
    if "chatbot" not in st.session_state or st.session_state.chatbot is None:
        try:
            from rag_chatbot import RAGChatbot
            chatbot = RAGChatbot()
            if chatbot.setup_retrieval_chain():
                st.session_state.chatbot = chatbot
                return True
            else:
                return False
        except Exception as e:
            st.error(f"Error inicializando chatbot: {e}")
            return False
    return True

# Inicializar estados de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

def main():
    # Verificar configuración primero
    if not check_configuration():
        return
    
    # Header principal
    st.markdown('<h1 class="main-header">🤖 Chatbot RAG - Documentos PDF</h1>', unsafe_allow_html=True)
    
    # Verificar si el sistema está listo
    system_ready, num_vectors = check_system_ready()
    
    if not system_ready:
        st.markdown("""
        <div class="error-box">
            <strong>⚠️ Sistema no está listo</strong><br>
            La base de conocimiento no está disponible. Contacta al administrador del sistema.
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        ### 📝 Información del Sistema
        
        Este chatbot necesita que la base de conocimiento esté configurada previamente.
        
        **Estado actual:** Base de datos vectorial vacía o no disponible
        
        **Para administradores:** Ejecuta `python process_and_store.py` para procesar los documentos.
        """)
        return
    
    # Inicializar chatbot
    if not initialize_chatbot():
        st.error("❌ Error inicializando el chatbot")
        return
    
    # Información del sistema en sidebar (opcional y minimalista)
    with st.sidebar:
        st.markdown("### 📊 Estado del Sistema")
        st.markdown(f'<div class="success-box">✅ Sistema operativo<br>{num_vectors} documentos cargados</div>', unsafe_allow_html=True)
        
        if st.button("🔄 Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Área principal de chat
    st.markdown("### 💬 Haz preguntas sobre los documentos")
    
    # Mostrar historial de mensajes
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar fuentes si es una respuesta del asistente
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander(f"📄 Ver fuentes ({len(message['sources'])})"):
                    for i, source in enumerate(message["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>{i}. 📄 {source['filename']}</strong> (fragmento {source['chunk_id']})<br>
                            <em>{source['preview']}</em>
                        </div>
                        """, unsafe_allow_html=True)
    
    # Input para nueva pregunta
    if prompt := st.chat_input("Escribe tu pregunta aquí..."):
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generar respuesta
        with st.chat_message("assistant"):
            with st.spinner("🤔 Analizando documentos..."):
                response = st.session_state.chatbot.chat(prompt)
            
            st.markdown(response["answer"])
            
            # Mostrar fuentes
            if response["sources"]:
                with st.expander(f"📄 Ver fuentes ({len(response['sources'])})"):
                    for i, source in enumerate(response["sources"], 1):
                        st.markdown(f"""
                        <div class="source-box">
                            <strong>{i}. 📄 {source['filename']}</strong> (fragmento {source['chunk_id']})<br>
                            <em>{source['preview']}</em>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Agregar respuesta al historial
        st.session_state.messages.append({
            "role": "assistant", 
            "content": response["answer"],
            "sources": response["sources"]
        })
    
    # Mensaje de ayuda al final
    if len(st.session_state.messages) == 0:
        st.markdown("""
        ### 💡 Ejemplos de preguntas:
        - "¿Cuáles son los puntos principales de estos documentos?"
        - "Resume la información sobre [tema específico]"
        - "¿Qué documentos hablan de [concepto]?"
        - "Explícame [término] mencionado en los documentos"
        """)

if __name__ == "__main__":
    main()