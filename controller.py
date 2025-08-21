"""
O orquestrador que executa o plano.
"""

from planner import RPGPlanner
from tools import search_lore, search_web


class Controller:
    def __init__(self, rpg_system:str):

        if not rpg_system:
            raise ValueError("O sistema de RPG deve ser fornecido.")

        self.rpg_system = rpg_system
        self.planner = RPGPlanner()
        self.context_data = {}

    def execute_task(self, user_prompt:str):
        """
              Orquestra todo o processo: planejar, executar cada passo e sintetizar a resposta.
              """
        # 1. Modelo cria o plano inicial
        try:
            plan = self.planner.create_plan(user_prompt, self.rpg_system)
            print(f"\nPlano Gerado: {plan}")
        except Exception as e:
            return f"Erro ao gerar o plano: {e}"

        # 2. Loop de execução do plano
        for step in plan:
            tool_to_use = step.get('tool')
            query = step.get('query')

            if not tool_to_use or not query:
                print(f"Passo inválido no plano, pulando: {step}")
                continue

            print(f"\nExecutando passo: Usar '{tool_to_use}' com a query '{query}'")

            # 3. Controlador chama a ferramenta de Percepção correta
            result = ""
            if tool_to_use == 'search_lore':
                result = search_lore(query, self.rpg_system)
            elif tool_to_use == 'search_web':
                result = search_web(query)
            else:
                result = f"Ferramenta '{tool_to_use}' desconhecida."

            self.context_data[query] = result

        # 4. Modelo gera a resposta final com os dados coletados
        final_response = self.planner.synthesize_answer(user_prompt, self.context_data)
        print(f"final_response {final_response}")
        return final_response
