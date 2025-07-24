# document_processor.py (Versión Local Simplificada)
import os
from typing import List
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
from config import Config

class DocumentProcessor:
    def __init__(self):
        self.config = Config()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def get_pdf_files(self) -> List[str]:
        """Obtiene lista de archivos PDF de la carpeta local"""
        pdf_files = []
        documents_folder = self.config.DOCUMENTS_FOLDER
        
        if not os.path.exists(documents_folder):
            print(f"❌ Carpeta {documents_folder} no existe")
            return pdf_files
        
        for filename in os.listdir(documents_folder):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(documents_folder, filename)
                pdf_files.append(pdf_path)
        
        print(f"📁 Encontrados {len(pdf_files)} archivos PDF")
        return pdf_files
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extrae texto de un archivo PDF"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                
                for page_num, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        text += f"\n--- Página {page_num + 1} ---\n"
                        text += page_text + "\n"
                
                return text
        
        except Exception as e:
            print(f"❌ Error procesando {pdf_path}: {e}")
            return ""
    
    def process_documents(self) -> List[Document]:
        """Procesa todos los documentos PDF de la carpeta local"""
        pdf_files = self.get_pdf_files()
        
        if not pdf_files:
            print("❌ No se encontraron archivos PDF")
            return []
        
        documents = []
        
        for pdf_path in pdf_files:
            filename = os.path.basename(pdf_path)
            print(f"🔄 Procesando: {filename}")
            
            # Extraer texto del PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            if text.strip():
                # Crear chunks del texto
                chunks = self.text_splitter.split_text(text)
                
                # Crear documentos con metadata
                for i, chunk in enumerate(chunks):
                    if chunk.strip():  # Solo chunks no vacíos
                        doc = Document(
                            page_content=chunk,
                            metadata={
                                "source": filename,
                                "file_path": pdf_path,
                                "chunk_id": i,
                                "total_chunks": len(chunks)
                            }
                        )
                        documents.append(doc)
                
                print(f"✅ {filename}: {len(chunks)} chunks creados")
            else:
                print(f"⚠️  {filename}: No se pudo extraer texto")
        
        print(f"🎉 Total: {len(documents)} chunks procesados de {len(pdf_files)} PDFs")
        return documents