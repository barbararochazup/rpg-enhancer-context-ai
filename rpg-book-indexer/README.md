
# PDF Vector Store Indexer

Este projeto tem como objetivo criar um índice vetorial (FAISS) a partir de documentos PDF, 
utilizando técnicas de NLP para dividir o texto em chunks, gerar embeddings e armazenar tudo em um índice eficiente para buscas semânticas.

## Funcionalidades 

- Carrega arquivos PDF e extrai o texto de cada página.
- Divide o texto em chunks com sobreposição para manter o contexto.
- Gera embeddings utilizando o modelo all-MiniLM-L6-v2 da HuggingFace.
- Cria e salva um índice vetorial FAISS localmente para consultas futuras.

## Como executar

### Pré-requisitos
- Python 3.9+

### Instalação

Instale as dependências:
```
cd rpg-book-rag-indexer
pip install -r requirements.txt
```

### Data
Coloque seu arquivo PDF em data/

```
 ../data/arquivo.pdf
```

**Obs.** Somente arquivos .pdf

### Execução

```
python indexer.py --file_path ../resources/data/arquivo.pdf
```

O índice será salvo em ```vector_stores/faiss_index_arquivo.```

### Tests

```
pytest rpg-book-indexer/
```

### Lint e Formatação de Código

Este projeto utiliza as seguintes ferramentas para garantir a qualidade e padronização do código Python:

- **isort**: Organiza e ordena automaticamente os imports.
```
isort .
```

- **autoflake**: Remove imports e variáveis não utilizadas.
```
autoflake --in-place --remove-unused-variables --remove-all-unused-imports -r .
```

- **black**: Formata o código automaticamente seguindo o padrão PEP 8.
```
black .
```

- **flake8**: Analisa o código e aponta problemas de estilo e possíveis erros.
```
flake8 .
```


### Comandos disponíveis via Makefile
Este projeto utiliza um Makefile para automatizar tarefas comuns de desenvolvimento. 
Abaixo estão os principais comandos disponíveis:


##### Instala as dependências do projeto listadas em requirements.txt
```
make install	
```
---

##### Remove imports e variáveis não utilizadas em todo o projeto.
```
make autoflake		
```
---

##### Organiza e ordena automaticamente os imports dos arquivos Python.
```
make isort		
```
--- 

##### Formata o código seguindo o padrão Black.
```
make black			
```
--- 

##### Executa o linter Flake8 para verificar problemas no código.
```
make flake8			
```
--- 

##### Executa todos os comandos de lint e formatação (autoflake, isort, black, flake8).

```
make lint
```
--- 

##### Executa os testes automatizados com pytest.

```
make test
```
--- 

##### Executa a aplicação principal (indexer.py). 
É necessário informar o caminho do arquivo PDF via variável FILE.
```
make run FILE=../data/book.pdf
```

--- 

## Como funciona

1. **Carregamento do PDF:** O arquivo PDF é carregado e o texto de cada página é extraído.

2. **Divisão em Chunks:** O texto é dividido em pedaços de 1000 caracteres, com sobreposição de 150 caracteres para manter o contexto.

3. **Geração de Embeddings:** Cada chunk é transformado em um vetor numérico usando o modelo all-MiniLM-L6-v2.

4. **Criação do Índice FAISS:** Todos os vetores são armazenados em um índice FAISS, que é salvo localmente para buscas rápidas.


## Dependências
- langchain
- langchain-community
- faiss-cpu
- huggingface_hub

## Observações
- O modelo de embeddings é baixado automaticamente na primeira execução.
- O índice FAISS é salvo na pasta vector_stores/ com o nome baseado no arquivo PDF.
