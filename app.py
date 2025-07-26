# app.py - Interfaz Streamlit con enlaces a PDFs optimizado
import streamlit as st
import os
from config import Config
import time
import warnings
import base64
from pathlib import Path

warnings.filterwarnings("ignore", message="No secrets files found")

# Configuración de la página
st.set_page_config(
    page_title="🤖 ILAR Chatbot",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    .pdf-info {
        display: inline-block;
        margin-top: 0.5rem;
        padding: 0.3rem 0.8rem;
        background-color: #f8f9fa;
        color: #495057;
        border-radius: 0.3rem;
        font-size: 0.8rem;
        border: 1px solid #dee2e6;
    }
    .pdf-download-btn {
        margin-left: 0.5rem;
        font-size: 0.8rem;
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
    .file-info {
        font-size: 0.7rem;
        color: #6c757d;
        margin-top: 0.2rem;
    }
</style>
""", unsafe_allow_html=True)

def get_file_size(file_path):
    """Obtiene el tamaño del archivo en formato legible"""
    try:
        size_bytes = os.path.getsize(file_path)
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024**2:
            return f"{size_bytes/1024:.1f} KB"
        else:
            return f"{size_bytes/(1024**2):.1f} MB"
    except:
        return "Tamaño desconocido"

def create_pdf_button_for_source(file_path, filename, unique_key):
    """Crea un botón de descarga para el PDF en las fuentes"""
    try:
        file_size = get_file_size(file_path)
        size_bytes = os.path.getsize(file_path)
        
        # Crear un contenedor único para el botón
        button_container = st.container()
        
        with button_container:
            # Leer el archivo PDF
            with open(file_path, "rb") as f:
                pdf_data = f.read()
            
            # Crear botón de descarga
            download_button = st.download_button(
                label=f"📄 Abrir {filename} ({file_size})",
                data=pdf_data,
                file_name=filename,
                mime="application/pdf",
                key=f"pdf_source_{unique_key}_{filename}",
                help=f"Haz clic para descargar/abrir {filename}"
            )
            
            return True
            
    except Exception as e:
        st.markdown(f'<span style="color: #6c757d; font-size: 0.8rem;">📄 {filename} - ❌ No disponible</span>', unsafe_allow_html=True)
        return False

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

def get_available_pdfs():
    """Obtiene la lista de PDFs disponibles con sus rutas"""
    try:
        config = Config()
        documents_folder = config.DOCUMENTS_FOLDER
        
        if not os.path.exists(documents_folder):
            return {}
        
        pdf_files = {}
        for filename in os.listdir(documents_folder):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(documents_folder, filename)
                pdf_files[filename] = pdf_path
        
        return pdf_files
    except Exception as e:
        st.error(f"Error obteniendo PDFs: {e}")
        return {}

# Inicializar estados de sesión
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chatbot" not in st.session_state:
    st.session_state.chatbot = None

def display_source_with_file_info(source, available_pdfs, message_index, source_index):
    """Muestra una fuente con botón de descarga del PDF"""
    filename = source['filename']
    
    # Mostrar información básica de la fuente
    st.markdown(f"""
    **📄 {filename}** (fragmento {source['chunk_id']})
    
    *{source['preview']}*
    """)
    
    # Agregar botón de descarga si el archivo está disponible
    if filename in available_pdfs:
        unique_key = f"{message_index}_{source_index}"
        create_pdf_button_for_source(available_pdfs[filename], filename, unique_key)
    else:
        st.markdown(f'<span style="color: #6c757d; font-size: 0.8rem;">📄 {filename} - ❌ Archivo no encontrado</span>', unsafe_allow_html=True)

def main():
    # Verificar configuración primero
    if not check_configuration():
        return
    
    # Header principal
    st.markdown('<h1 class="main-header">🤖 Chatbot ILAR </h1>', unsafe_allow_html=True)
    
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
    
    # Obtener PDFs disponibles
    available_pdfs = get_available_pdfs()
    
    # Información del sistema en sidebar
    with st.sidebar:
        st.markdown("### 📊 Estado del Sistema")
        st.markdown(f'<div class="success-box">✅ Sistema operativo<br>{num_vectors} documentos cargados</div>', unsafe_allow_html=True)
        
        # Mostrar solo información básica de los PDFs disponibles
        if available_pdfs:
            st.markdown("### 📚 Documentos Disponibles")
            for filename, filepath in available_pdfs.items():
                file_size = get_file_size(filepath)
                st.markdown(f"📄 **{filename}** ({file_size})")
        
        if st.button("🔄 Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
    
    # Área principal de chat
    st.markdown("### 💬 Haz preguntas sobre los documentos")
    
    # Mostrar historial de mensajes
    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Mostrar fuentes si es una respuesta del asistente
            if message["role"] == "assistant" and "sources" in message and message["sources"]:
                with st.expander(f"📄 Ver fuentes ({len(message['sources'])})"):
                    for source_index, source in enumerate(message["sources"]):
                        st.markdown(f"**{source_index + 1}.**")
                        display_source_with_file_info(source, available_pdfs, message_index, source_index)
                        st.markdown("---")
    
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
            
            # Mostrar fuentes con botones de descarga
            if response["sources"]:
                with st.expander(f"📄 Ver fuentes ({len(response['sources'])})"):
                    for source_index, source in enumerate(response["sources"]):
                        st.markdown(f"**{source_index + 1}.**")
                        # Crear key único para el mensaje actual
                        current_message_index = len(st.session_state.messages)
                        display_source_with_file_info(source, available_pdfs, current_message_index, source_index)
                        st.markdown("---")
        
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