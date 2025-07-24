# process_and_store.py
from document_processor import DocumentProcessor
from vector_store import VectorStoreManager

def main():
    print("🚀 Iniciando procesamiento de documentos...")
    
    # 1. Procesar documentos PDF
    print("\n📄 Paso 1: Procesando documentos PDF...")
    processor = DocumentProcessor()
    documents = processor.process_documents()
    
    if not documents:
        print("❌ No se procesaron documentos. Verifica que tengas PDFs en la carpeta 'documentos'")
        return
    
    # 2. Almacenar en base vectorial
    print("\n🗄️ Paso 2: Almacenando en base vectorial...")
    vector_manager = VectorStoreManager()
    success = vector_manager.store_documents(documents)
    
    if success:
        # 3. Verificar almacenamiento
        print("\n📊 Paso 3: Verificando almacenamiento...")
        stats = vector_manager.get_index_stats()
        print(f"✅ Total de vectores almacenados: {stats.get('total_vectors', 0)}")
        print(f"✅ Dimensión de vectores: {stats.get('dimension', 0)}")
        
        # 4. Prueba rápida de búsqueda
        print("\n🔍 Paso 4: Prueba de búsqueda...")
        test_query = "¿Qué información contienen estos documentos?"
        results = vector_manager.search_similar_documents(test_query, k=2)
        
        if results:
            print(f"✅ Búsqueda exitosa! Encontrados {len(results)} resultados relevantes")
            for i, doc in enumerate(results, 1):
                source = doc.metadata.get('source', 'Desconocido')
                preview = doc.page_content[:100] + "..."
                print(f"  {i}. 📄 {source}: {preview}")
        else:
            print("⚠️  No se encontraron resultados en la búsqueda de prueba")
        
        print("\n🎉 ¡Procesamiento completado exitosamente!")
        print("💡 Ya puedes usar el chatbot con estos documentos")
    
    else:
        print("❌ Error en el almacenamiento")

if __name__ == "__main__":
    main()