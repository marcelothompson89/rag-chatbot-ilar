# app.py - Interfaz Streamlit con verificación de configuración
import streamlit as st
import os
from config import Config
import time

# Configuración de la página
st.set_page_config(
    page_title="🤖 RAG Chatbot - Documentos PDF",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
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
    .warning-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #ffeaa7;
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
    config = Config()
    errors = config.validate_keys()
    
    if errors:
        st.markdown('<h1 class="main-header">⚙️ Configuración Requerida</h1>', unsafe_allow_html=True)
        
        st.markdown(f'<div class="error-box"><strong>❌ Configuración Incompleta</strong><br>{"<br>".join(errors)}</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🔧 Para configurar las API Keys en Streamlit Cloud:
        
        1. **Ve a tu aplicación en Streamlit Cloud**
        2. **Haz clic en "Manage app"** (esquina inferior derecha)
        3. **Ve a la pestaña "Settings"**
        4. **Selecciona "Secrets"**
        5. **Agrega las siguientes variables:**
        
        ```toml
        OPENAI_API_KEY = "tu-api-key-real-de-openai"
        PINECONE_API_KEY = "tu-api-key-real-de-pinecone"
        DOCUMENTS_FOLDER = "documentos"
        ```
        
        6. **Guarda los cambios**
        7. **La aplicación se reiniciará automáticamente**
        
        ### 📝 Notas importantes:
        - No incluyas las comillas en las API keys
        - Las API keys deben ser reales, no placeholders
        - Después de guardar, espera unos segundos para que se reinicie
        """)
        
        return False
    
    return True

# Inicializar estados de sesión
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "system_ready" not in st.session_state:
    st.session_state.system_ready = False
if "documents_processed" not in st.session_state:
    st.session_state.documents_processed = False

def check_documents():
    """Verifica si hay documentos en la carpeta"""
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        pdf_files = processor.get_pdf_files()
        return len(pdf_files) > 0, len(pdf_files)
    except Exception as e:
        st.error(f"Error verificando documentos: {e}")
        return False, 0

def process_documents():
    """Procesa y almacena documentos"""
    try:
        with st.spinner("🔄 Procesando documentos PDF..."):
            # Procesar documentos
            from document_processor import DocumentProcessor
            processor = DocumentProcessor()
            documents = processor.process_documents()
            
            if documents:
                # Almacenar en vector store
                from vector_store import VectorStoreManager
                vector_manager = VectorStoreManager()
                success = vector_manager.store_documents(documents)
                
                if success:
                    st.session_state.documents_processed = True
                    return True, len(documents)
                else:
                    return False, 0
            else:
                return False, 0
    except Exception as e:
        st.error(f"Error procesando documentos: {e}")
        return False, 0

def initialize_chatbot():
    """Inicializa el chatbot"""
    try:
        with st.spinner("🤖 Inicializando chatbot..."):
            from rag_chatbot import RAGChatbot
            chatbot = RAGChatbot()
            if chatbot.setup_retrieval_chain():
                st.session_state.chatbot = chatbot
                st.session_state.system_ready = True
                return True
            else:
                return False
    except Exception as e:
        st.error(f"Error inicializando chatbot: {e}")
        return False

def main():
    # Verificar configuración primero
    if not check_configuration():
        return
    
    # Header principal
    st.markdown('<h1 class="main-header">🤖 RAG Chatbot para Documentos PDF</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar para configuración y estado
    with st.sidebar:
        st.header("⚙️ Panel de Control")
        
        # 1. Verificar documentos
        st.subheader("📁 Documentos")
        has_docs, num_docs = check_documents()
        
        if has_docs:
            st.markdown(f'<div class="success-box">✅ {num_docs} documentos PDF encontrados</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="warning-box">⚠️ No hay documentos PDF en la carpeta "documentos"<br>Agrega algunos archivos PDF y recarga la página.</div>', unsafe_allow_html=True)
            st.stop()
        
        # 2. Estado del procesamiento
        st.subheader("🗄️ Base de Conocimiento")
        
        if not st.session_state.documents_processed:
            if st.button("📥 Procesar Documentos", type="primary"):
                success, num_chunks = process_documents()
                if success:
                    st.success(f"✅ {num_chunks} chunks procesados y almacenados")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error procesando documentos")
        else:
            st.markdown('<div class="success-box">✅ Documentos procesados y almacenados</div>', unsafe_allow_html=True)
        
        # 3. Estado del chatbot
        st.subheader("🤖 Chatbot")
        
        if not st.session_state.system_ready and st.session_state.documents_processed:
            if st.button("🚀 Inicializar Chatbot", type="primary"):
                if initialize_chatbot():
                    st.success("✅ Chatbot listo")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Error inicializando chatbot")
        elif st.session_state.system_ready:
            st.markdown('<div class="success-box">✅ Chatbot operativo</div>', unsafe_allow_html=True)
            
            # Estadísticas del sistema
            if st.session_state.chatbot:
                stats = st.session_state.chatbot.get_system_stats()
                with st.expander("📊 Estadísticas del Sistema"):
                    st.write(f"**Documentos:** {stats.get('total_documents', 'N/A')}")
                    st.write(f"**Modelo:** {stats.get('model_used', 'N/A')}")
                    st.write(f"**Estado:** {stats.get('status', 'N/A')}")
        
        # Botón de reinicio
        st.markdown("---")
        if st.button("🔄 Reiniciar Sistema"):
            st.session_state.clear()
            st.rerun()
        
        # Información adicional
        with st.expander("💡 Cómo usar"):
            st.markdown("""
            **Pasos para usar el chatbot:**
            
            1. **Coloca tus PDFs** en la carpeta `documentos/`
            2. **Procesa los documentos** (botón azul)
            3. **Inicializa el chatbot** (botón azul)
            4. **¡Empieza a chatear!** 
            
            **Ejemplos de preguntas:**
            - "¿Qué información contienen estos documentos?"
            - "Resume los puntos principales"
            - "¿Hay información sobre [tema específico]?"
            """)
    
    # Área principal de chat
    if st.session_state.system_ready and st.session_state.chatbot:
        st.header("💬 Chat con tus Documentos")
        
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
                                <strong>{i}. 📄 {source['filename']}</strong> (chunk {source['chunk_id']})<br>
                                <em>{source['preview']}</em>
                            </div>
                            """, unsafe_allow_html=True)
        
        # Input para nueva pregunta
        if prompt := st.chat_input("Haz una pregunta sobre tus documentos..."):
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
                                <strong>{i}. 📄 {source['filename']}</strong> (chunk {source['chunk_id']})<br>
                                <em>{source['preview']}</em>
                            </div>
                            """, unsafe_allow_html=True)
            
            # Agregar respuesta al historial
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["answer"],
                "sources": response["sources"]
            })
    
    elif st.session_state.documents_processed and not st.session_state.system_ready:
        st.info("👆 Usa el panel lateral para inicializar el chatbot")
    
    elif has_docs and not st.session_state.documents_processed:
        st.info("👆 Usa el panel lateral para procesar los documentos")
    
    else:
        st.markdown("""
        ## 🚀 ¡Bienvenido al RAG Chatbot!
        
        Este sistema te permite chatear con tus documentos PDF usando inteligencia artificial.
        
        ### 📋 Para empezar:
        1. **Agrega documentos PDF** a la carpeta `documentos/` de tu proyecto
        2. **Usa el panel lateral** para procesar los documentos
        3. **Inicializa el chatbot** cuando esté listo
        4. **¡Empieza a hacer preguntas!**
        
        ### 💡 Ejemplos de preguntas que puedes hacer:
        - "¿Cuáles son los puntos principales de estos documentos?"
        - "Resume la información sobre [tema específico]"
        - "¿Qué documentos hablan de [concepto]?"
        - "Explícame [término o proceso] mencionado en los documentos"
        
        ### ✨ Características:
        - 🎯 **Respuestas precisas** basadas en tus documentos
        - 📚 **Referencias a fuentes** en cada respuesta
        - 🔍 **Búsqueda semántica** avanzada
        - 💬 **Chat conversacional** natural
        """)

if __name__ == "__main__":
    main()