# run_app.py
import subprocess
import sys
import os

def check_requirements():
    """Verifica que todo esté configurado"""
    print("🔍 Verificando requisitos...")
    
    # Verificar archivos necesarios
    required_files = [
        'config.py',
        'document_processor.py', 
        'vector_store.py',
        'rag_chatbot.py',
        'app.py',
        '.env'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Archivos faltantes: {', '.join(missing_files)}")
        return False
    
    # Verificar carpeta documentos
    if not os.path.exists('documentos'):
        print("❌ Carpeta 'documentos' no existe")
        print("💡 Ejecuta: mkdir documentos")
        return False
    
    # Verificar que hay PDFs
    pdf_files = [f for f in os.listdir('documentos') if f.lower().endswith('.pdf')]
    if not pdf_files:
        print("⚠️  No hay archivos PDF en la carpeta 'documentos'")
        print("💡 Agrega algunos archivos PDF a la carpeta 'documentos'")
        return False
    
    print(f"✅ {len(pdf_files)} archivos PDF encontrados")
    
    # Verificar archivo .env
    try:
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'pendiente-configurar' in env_content or 'your-' in env_content:
                print("⚠️  Archivo .env no configurado completamente")
                print("💡 Edita el archivo .env con tus API keys reales")
                return False
    except:
        print("❌ Error leyendo archivo .env")
        return False
    
    print("✅ Configuración verificada")
    return True

def run_streamlit():
    """Ejecuta la aplicación Streamlit"""
    print("🚀 Iniciando aplicación web...")
    print("🌐 La aplicación se abrirá en tu navegador")
    print("📝 Para detener la aplicación, presiona Ctrl+C")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.runOnSave", "true",
            "--theme.base", "light"
        ])
    except KeyboardInterrupt:
        print("\n👋 Aplicación detenida")
    except Exception as e:
        print(f"❌ Error ejecutando aplicación: {e}")

def main():
    print("🤖 RAG Chatbot - Launcher")
    print("=" * 40)
    
    if check_requirements():
        print("\n🎉 Todo listo para ejecutar la aplicación")
        
        response = input("\n¿Ejecutar la aplicación web? (s/n): ").strip().lower()
        if response in ['s', 'si', 'sí', 'y', 'yes']:
            run_streamlit()
        else:
            print("💡 Para ejecutar manualmente: streamlit run app.py")
    else:
        print("\n❌ Por favor, corrige los problemas antes de continuar")
        print("💡 Revisa los mensajes de error arriba")

if __name__ == "__main__":
    main()