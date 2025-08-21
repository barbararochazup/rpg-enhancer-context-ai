import os.path

import argparse
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings

def create_vector_store(file_path: str):
    """Carrega um documento, divide em chunks, cria embeddings e salva em um índice FAISS."""

    print(f"Carregando documento de:  {file_path}")
    if not os.path.exists(file_path):
        print(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    file_name = os.path.basename(file_path)
    index_name_prefix = os.path.splitext(file_name)[0].lower().replace(" ", "_")  # Substitui espaços por underscores
    index_path = f"vector_stores/faiss_index_{index_name_prefix}"

    pages = loading_docs(file_name, file_path)

    docs = load_chunks(file_name, pages)

    embeddings = create_embeddings()

    create_and_save_faiss_index(index_path, docs, embeddings)


def loading_docs(file_name, file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load() # retorna lista de documentos
    print(f"Documento {file_name} carregado. O documento tem {len(pages)} páginas.")
    return pages

def load_chunks(file_name, pages):
    print(f"Dividindo o documento {file_name} em chunks menores...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # tam de cada chuck de texto
        chunk_overlap=150  # Sopreposiçao entre chuncks para nao perder contexto
    )
    docs = text_splitter.split_documents(pages)
    print(f"O documento {file_name} foi dividido em {len(docs)} chunks para vetorização.")
    return docs

def create_embeddings():
    print("Criando embeddings com 'all-MiniLM-L6-v2'. Isso pode levar alguns minutos...")
    return HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def create_and_save_faiss_index(index_path, docs, embeddings):
    print(f"Criando e salvando o índice FAISS em: {index_path}")
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(index_path)
    print("Índice criado com sucesso!")


if __name__ == "__main__":
    # Para executar: python build_rag_index.py --file_path "data/tormenta20_lore.txt" --index_path "vector_stores/faiss_index_tormenta20"
    parser = argparse.ArgumentParser(description="Cria um índice vetorial a partir de um arquivo de texto.")
    parser.add_argument("--file_path", type=str, required=True, help="Caminho para o arquivo .txt com o lore.")
    args = parser.parse_args()
    create_vector_store(args.file_path)




