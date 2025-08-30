
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

"""
 Define as "ferramentas" que o agente pode usar.
"""

load_dotenv()

embeddings_model = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')

def search_lore(query: str, rpg_system: str) -> str:
    """
      Busca informações em uma base de conhecimento vetorial (RAG).
      """
    index_path = f"vector_stores/faiss_index_{rpg_system.lower()}"
    if not os.path.exists(index_path):
        return f"Erro: Índice para o sistema '{rpg_system}' não encontrado em '{index_path}'."

    print(f"--- Usando Ferramenta RAG: Buscando '{query}' em '{rpg_system}' ---")

    # Carrega o índice FAISS do disco
    db = FAISS.load_local(index_path, embeddings_model)

    # Realiza a busca por similaridade
    results = db.similarity_search(query, k=5)  # Pega os 2 chunks mais relevantes

    # Concatena os resultados em uma única string de contexto
    context = "\n".join([doc.page_content for doc in results])
    return context

def search_web(query: str):
    """
     Realiza uma busca na web usando a Google Custom Search API.
     """
    print(f"--- Usando Ferramenta Web (Real): Buscando '{query}' ---")
    try:
        # Pega as credenciais do ambiente
        api_key = os.getenv("GOOGLE_API_KEY")
        search_engine_id = os.getenv("SEARCH_ENGINE_ID")

        if not api_key or not search_engine_id:
            return "Erro: GOOGLE_API_KEY ou SEARCH_ENGINE_ID não encontrados no arquivo .env."

        # Constrói o serviço da API
        service = build("customsearch", "v1", developerKey=api_key)

        # Executa a requisição de busca
        res = service.cse().list(
            q=query,
            cx=search_engine_id,
            num=3  # Pede os 3 principais resultados
        ).execute()

        # Extrai os snippets dos resultados
        items = res.get('items', [])
        if not items:
            return "Nenhum resultado encontrado na web para esta busca."

        # Formata os snippets em uma string de contexto
        snippets = [f"Fonte: {item['link']}\nResumo: {item['snippet']}" for item in items]

        return "\n\n".join(snippets)

    except Exception as e:
        return f"Ocorreu um erro ao buscar na web: {e}"




