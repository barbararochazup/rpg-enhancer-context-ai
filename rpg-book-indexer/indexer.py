import argparse
import logging
import os.path
from pathlib import Path
from typing import List

from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

# Configuração log
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)


def create_vector_store(file_path: Path) -> None:
    """
    Carrega um documento, divide em chunks, cria embeddings e salva em um índice FAISS.
    """

    # Verifica se o arquivo existe
    if not os.path.exists(file_path):
        logging.error(f"Erro: O arquivo '{file_path}' não foi encontrado.")
        return

    file_name = file_path.name
    # Gera o nome do índice baseado no nome do arquivo, removendo espaços e deixando minúsculo
    index_name_prefix = os.path.splitext(file_name)[0].lower().replace(" ", "_")
    index_path = Path("../resources/vector_stores") / f"faiss_index_{index_name_prefix}"

    pages = load_docs(file_path)  # Carrega as páginas do PDF
    chunks = split_chunks(
        pages, file_name
    )  # Divide as páginas em chunks menores para melhor vetorização
    embeddings = (
        create_embeddings()
    )  # Cria o objeto de embeddings (modelo de linguagem)
    create_and_save_faiss_index(
        index_path, chunks, embeddings
    )  # Cria e salva o índice FAISS localmente


def load_docs(file_path: Path) -> List:
    """
    Carrega o PDF e retorna uma lista de páginas/documentos.
    """
    logging.info(f"### Carregando documento {file_path.name} ...")
    loader = PyPDFLoader(
        str(file_path)
    )  # Usa o PyPDFLoader da LangChain para ler o PDF
    pages = loader.load()
    logging.info(
        f"Documento {file_path.name} carregado. O documento tem {len(pages)} páginas."
    )
    return pages


def split_chunks(pages: List, file_name: str) -> List:
    """
    Divide o documento em chunks menores para vetorização.
    """
    logging.info(f"### Dividindo o documento {file_name}  em chunks menores ...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # Tamanho de cada chunk de texto
        chunk_overlap=150,  # Sobreposição entre chunks para manter contexto
    )
    docs = text_splitter.split_documents(pages)  # Divide as páginas em chunks menores
    logging.info(
        f"O documento {file_name} foi dividido em {len(docs)} chunks para vetorização."
    )
    return docs


def create_embeddings() -> HuggingFaceEmbeddings:
    load_dotenv()  # Carrega as variáveis do .env
    model_name = os.getenv("EMBEDDINGS_MODEL", "all-MiniLM-L6-v2")
    logging.info(
        f"### Criando embeddings com '{model_name}'. Isso pode levar alguns minutos..."
    )
    try:
        return HuggingFaceEmbeddings(model_name=model_name)
    except Exception as e:
        logging.error(f"Erro ao criar embeddings com o modelo '{model_name}': {e}")
        raise ValueError(
            f"Não foi possível carregar o modelo de embeddings '{model_name}'. "
            f"Verifique se o nome está correto e se o modelo está disponível."
        ) from e


def create_and_save_faiss_index(
    index_path: Path, chunks: List, embeddings: HuggingFaceEmbeddings
):
    """
    Cria e salva o índice FAISS.
    """
    logging.info(f"### Criando e salvando o índice FAISS em: {index_path} ...")
    db = FAISS.from_documents(
        chunks, embeddings
    )  # Cria o índice FAISS a partir dos chunks e embeddings
    db.save_local(index_path)  # Salva o índice localmente
    logging.info(f"Índice FAISS salvo em: {index_path}")


def parse_args():
    # Configura o parser de argumentos para receber o caminho do arquivo PDF
    parser = argparse.ArgumentParser(
        description="Cria um índice vetorial a partir de um arquivo PDF."
    )
    parser.add_argument(
        "--file_path", type=Path, required=True, help="Caminho para o arquivo .pdf"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    create_vector_store(args.file_path)
