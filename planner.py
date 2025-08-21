"""
O "cérebro" que usa o LLM para criar o plano e sintetizar a resposta.
"""
import json
import os
import re
import time

from langchain_core.messages import SystemMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()


class RPGPlanner:
    def __init__(self):
        # Validação para garantir que a chave de API foi encontrada
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("A chave de API do Google (GOOGLE_API_KEY) não foi encontrada no ambiente.")
        self.llm_manager = LLMClientManager()

    def create_plan(self, user_prompt: str, rpg_system: str):
        """
        Usa o LLM para analisar o pedido do usuário e gerar um plano de ação em JSON.
        """

        # O prompt de sistema que ensina o LLM a ser um planejador
        system_prompt = """
               Você é um planejador especialista para um assistente de apoio criação de personagens, aventuras e cenários de RPG. 
               Seu trabalho é analisar o pedido do usuário e dividi-lo em uma lista de passos de pesquisa claros e objetivos em formato JSON.

               Você tem acesso a DUAS ferramentas:
               1. `search_lore`: Use esta ferramenta para buscar informações específicas do universo do jogo (personagens, lugares, regras, história).
               2. `search_web`: Use esta ferramenta para buscar informações do mundo real (contexto histórico, científico, cultural).

               Responda APENAS com o JSON.

               Exemplo 1:
               - Pedido: "Crie um anão ferreiro de 80 anos em Vectora para Tormenta20."
               - Sistema: "Tormenta20"
               - JSON: [{"tool": "search_lore", "query": "Descrição da cidade de Vectora em Tormenta20"}, {"tool": "search_lore", "query": "Cultura e tradições dos anões em Tormenta20"}]

               Exemplo 2:
               - Pedido: "Crie um investigador no Brasil em 1943."
               - Sistema: "Chamado de Cthulhu"
               - JSON: [{"tool": "search_web", "query": "Contexto político e social do Brasil em 1943"}, {"tool": "search_web", "query": "Moda e costumes no Brasil em 1943"}]
               """

        formatted_prompt = f"Pedido: \"{user_prompt}\"\nSistema: \"{rpg_system}\""

        print("\n--- Gerando plano com o LLM... ---")
        response = self.llm_manager.invoke_with_rate_limit(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=formatted_prompt)
            ],
            temperature=0.0
        )

        clean_response = re.sub(r"```[a-z]*\n?", "", response.content).strip()
        clean_response = clean_response.encode("utf-8",  "ignore").decode("utf-8")   # Corrige caracteres inválidos de encoding

        # for i, c in enumerate(clean_response):
        #     try:
        #         c.encode("utf-8")
        #     except UnicodeEncodeError:
        #         print(f"Caractere inválido na posição {i}: {repr(c)}")

        plan_obj = json.loads(clean_response)
        return plan_obj

    def synthesize_answer(self, user_prompt: str, context_data: dict) -> str:
        """
            Usa o LLM para gerar uma resposta final coesa, usando os dados coletados.
        """

        system_prompt = "Você é um nerd de RPG prestativo. Sua tarefa é responder ao pedido do jogador de forma criativa e informativa, usando o contexto fornecido. Seja direto e organize a resposta de forma clara."

        # Formata todo o contexto coletado para enviar ao LLM
        context_str = "\n\n---\n\n".join(
            f"Resultado da pesquisa para '{query}':\n{data}" for query, data in context_data.items()
        )

        formatted_prompt = f"""
              Pedido Original do Jogador: "{user_prompt}"

              --- CONTEXTO COLETADO ---
              {context_str}
              --- FIM DO CONTEXTO ---

              Com base no contexto acima, responda ao pedido original do jogador.
              """

        print("\n--- Sintetizando resposta final com o LLM... ---")

        response = self.llm_manager.invoke_with_rate_limit(
            [
                SystemMessage(content=system_prompt),
                HumanMessage(content=formatted_prompt)
            ],
            temperature=0.7
        )

        return response.content


class LLMClientManager:
    """
    Esta classe garante que teremos apenas UMA instância do cliente LLM
    em toda a aplicação (padrão Singleton) e controla a frequência das chamadas.
    """
    _instance = None

    # Define o tempo mínimo em segundos entre as chamadas de API
    REQUEST_INTERVAL = 3  # 3 segundos = 20 chamadas por minuto (seguro para o free tier)

    def __init__(self):
        self.last_call_time = 0

    def __new__(cls):
        if cls._instance is None:
            print("--- Inicializando o Gerenciador de Cliente LLM (apenas uma vez) ---")
            cls._instance = super(LLMClientManager, cls).__new__(cls)

            if not os.getenv("GOOGLE_API_KEY"):
                raise ValueError("A chave de API do Google (GOOGLE_API_KEY) não foi encontrada.")

            # --- PASSO 1: UNIFICAR OS CLIENTES LLM EM UM SÓ ---
            cls._instance.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-pro",
                max_retries=2
            )
            cls._instance.last_call_time = 0
        return cls._instance

    def invoke_with_rate_limit(self, prompt, temperature: float):
        """
        Executa a chamada à API, garantindo que o intervalo mínimo seja respeitado.
        """
        current_time = time.time()
        elapsed_time = current_time - self.last_call_time

        if elapsed_time < self.REQUEST_INTERVAL:
            wait_time = self.REQUEST_INTERVAL - elapsed_time
            print(f"--- Rate Limiter: Aguardando {wait_time:.2f} segundos... ---")
            time.sleep(wait_time)

        # Passamos a temperatura dinamicamente na hora da chamada
        response = self.llm.invoke(prompt, temperature=temperature)

        self.last_call_time = time.time()
        return response