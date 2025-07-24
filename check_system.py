# check_system.py
def check_complete_system():
    print("🔍 Verificando sistema completo RAG...")
    
    # 1. Verificar configuración
    print("\n1️⃣ Verificando configuración...")
    try:
        from config import Config
        config = Config()
        
        if config.OPENAI_API_KEY and not config.OPENAI_API_KEY.startswith('sk-your'):
            print("✅ OpenAI API Key configurada")
        else:
            print("❌ OpenAI API Key no configurada")
            return False
            
        if config.PINECONE_API_KEY and not config.PINECONE_API_KEY.startswith('your'):
            print("✅ Pinecone API Key configurada")
        else:
            print("❌ Pinecone API Key no configurada")
            return False
            
    except Exception as e:
        print(f"❌ Error en configuración: {e}")
        return False
    
    # 2. Verificar documentos
    print("\n2️⃣ Verificando documentos...")
    try:
        from document_processor import DocumentProcessor
        processor = DocumentProcessor()
        pdf_files = processor.get_pdf_files()
        
        if pdf_files:
            print(f"✅ {len(pdf_files)} documentos PDF encontrados")
        else:
            print("❌ No hay documentos PDF en la carpeta")
            return False
            
    except Exception as e:
        print(f"❌ Error verificando documentos: {e}")
        return False
    
    # 3. Verificar base vectorial
    print("\n3️⃣ Verificando base vectorial...")
    try:
        from vector_store import VectorStoreManager
        vector_manager = VectorStoreManager()
        stats = vector_manager.get_index_stats()
        
        if stats.get('total_vectors', 0) > 0:
            print(f"✅ {stats['total_vectors']} vectores almacenados")
        else:
            print("❌ No hay vectores almacenados")
            print("💡 Ejecuta: python process_and_store.py")
            return False
            
    except Exception as e:
        print(f"❌ Error en base vectorial: {e}")
        return False
    
    # 4. Verificar chatbot
    print("\n4️⃣ Verificando chatbot...")
    try:
        from rag_chatbot import RAGChatbot
        chatbot = RAGChatbot()
        
        if chatbot.setup_retrieval_chain():
            print("✅ Chatbot configurado correctamente")
            
            # Prueba rápida
            if chatbot.test_system():
                print("✅ Prueba del chatbot exitosa")
            else:
                print("⚠️ Chatbot funciona pero con advertencias")
        else:
            print("❌ Error configurando chatbot")
            return False
            
    except Exception as e:
        print(f"❌ Error en chatbot: {e}")
        return False
    
    print("\n🎉 ¡Sistema completo verificado y funcionando!")
    print("💡 Puedes ejecutar: python test_chatbot.py")
    return True

if __name__ == "__main__":
    check_complete_system()