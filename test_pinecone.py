# test_pinecone.py
from vector_store import VectorStoreManager

def test_pinecone_connection():
    print("🔍 Verificando conexión a Pinecone...")
    
    try:
        vector_manager = VectorStoreManager()
        
        # Obtener estadísticas
        stats = vector_manager.get_index_stats()
        
        if "error" not in stats:
            print("✅ Conexión a Pinecone exitosa")
            print(f"✅ Índice activo: {vector_manager.config.INDEX_NAME}")
            print(f"📊 Vectores almacenados: {stats.get('total_vectors', 0)}")
            print(f"📐 Dimensión: {stats.get('dimension', 0)}")
        else:
            print(f"❌ Error: {stats['error']}")
    
    except Exception as e:
        print(f"❌ Error conectando a Pinecone: {e}")
        print("\n💡 Posibles soluciones:")
        print("1. Verifica tu PINECONE_API_KEY en el archivo .env")
        print("2. Asegúrate de tener una cuenta activa en Pinecone")
        print("3. Verifica tu conexión a internet")

if __name__ == "__main__":
    test_pinecone_connection()