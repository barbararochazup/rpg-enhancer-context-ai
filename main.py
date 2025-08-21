"""
  Ponto de entrada da aplicação. Lida com o input do usuário e inicia o controlador.
"""
from controller import Controller


def main():
    print("--- Bem-vindo ao RPG Context Enhancer! ---")
    print("Descreva o que você quer criar e para qual sistema de RPG.\n")

    try:
        rpg_system = input("Primeiro, informe o sistema de RPG (ex: Tormenta20, Cthulhu): ")
        user_prompt = input(f"Agora, descreva seu personagem/aventura/cenário para {rpg_system}: ")

        if not rpg_system or not user_prompt:
            print("Ambos os campos, sistema e pedido, são obrigatórios.")
            return

        # Inicia o controlador com o sistema de RPG especificado
        main_controller = Controller(rpg_system)

        # Executa a tarefa
        response = main_controller.execute_task(user_prompt)

        print("\n\n================= RESPOSTA FINAL =================\n")
        print(response)
        print("\n==================================================\n")

    except Exception as e:
        print(f"\nOcorreu um erro inesperado: {e}")


if __name__ == "__main__":
    main()