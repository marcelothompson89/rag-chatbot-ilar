# test_chatbot.py
from rag_chatbot import RAGChatbot

def test_chatbot():
    print("🤖 Probando el chatbot RAG...")
    
    # Crear instancia del chatbot
    chatbot = RAGChatbot()
    
    # Configurar la cadena RAG
    if not chatbot.setup_retrieval_chain():
        print("❌ No se pudo configurar el chatbot")
        return
    
    # Mostrar estadísticas del sistema
    stats = chatbot.get_system_stats()
    print(f"\n📊 Estadísticas del sistema:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Prueba automática
    print(f"\n🧪 Ejecutando prueba automática...")
    if chatbot.test_system():
        print("✅ Sistema funcionando correctamente")
    else:
        print("❌ Problemas detectados en el sistema")
        return
    
    # Preguntas de prueba interactivas
    test_questions = [
        "¿Qué información principal contienen estos documentos?",
        "¿Puedes hacer un resumen de los temas tratados?",
        "¿Qué documentos están disponibles?"
    ]
    
    print(f"\n💬 Probando con preguntas de ejemplo:")
    
    for i, question in enumerate(test_questions, 1):
        print(f"\n--- Pregunta {i} ---")
        print(f"❓ {question}")
        
        result = chatbot.chat(question)
        
        if result["success"]:
            print(f"🤖 {result['answer']}")
            
            if result["sources"]:
                print(f"\n📚 Fuentes ({len(result['sources'])}):")
                for j, source in enumerate(result['sources'], 1):
                    print(f"  {j}. 📄 {source['filename']} (chunk {source['chunk_id']})")
                    print(f"     Preview: {source['preview']}")
            else:
                print("📚 Sin fuentes específicas")
        else:
            print(f"❌ Error: {result['answer']}")
        
        print("-" * 50)

def interactive_chat():
    """Chat interactivo con el usuario"""
    print("\n🎉 ¡Chat interactivo activado!")
    print("💡 Haz preguntas sobre tus documentos (escribe 'salir' para terminar)")
    
    chatbot = RAGChatbot()
    if not chatbot.setup_retrieval_chain():
        print("❌ No se pudo inicializar el chatbot")
        return
    
    while True:
        try:
            question = input("\n🧑 Tu pregunta: ").strip()
            
            if question.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            if not question:
                print("💡 Por favor, escribe una pregunta")
                continue
            
            print("🤖 Pensando...")
            result = chatbot.chat(question)
            
            print(f"\n🤖 Respuesta:\n{result['answer']}")
            
            if result["sources"]:
                print(f"\n📚 Fuentes:")
                for i, source in enumerate(result['sources'], 1):
                    print(f"  {i}. 📄 {source['filename']}")
            
        except KeyboardInterrupt:
            print("\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Ejecutar pruebas
    test_chatbot()
    
    # Preguntar si quiere chat interactivo
    response = input("\n¿Quieres probar el chat interactivo? (s/n): ").strip().lower()
    if response in ['s', 'si', 'sí', 'y', 'yes']:
        interactive_chat()