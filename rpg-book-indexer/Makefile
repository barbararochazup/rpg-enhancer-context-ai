.PHONY: install lint format autoflake isort black flake8 test run build clean

# Instala as dependências do projeto
install:
	pip install -r requirements.txt

# Remove imports e variáveis não utilizadas
autoflake:
	autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .

# Organiza e ordena os imports
isort:
	isort .

# Formata o código
black:
	black .

# Verifica problemas de lint
flake8:
	flake8 .

# Executa os testes
test:
	pytest

# Executa a aplicação
run:
	python3 indexer.py --file_path $(FILE)