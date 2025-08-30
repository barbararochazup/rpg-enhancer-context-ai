import logging

import pytest
from reportlab.pdfgen import canvas

from indexer import create_embeddings, create_vector_store, load_docs, split_chunks


def test_load_docs_pdf(tmp_path):
    """
    Testa a função load_docs para garantir que ela carrega corretamente um PDF simples.

    - Cria um arquivo PDF temporário usando o reportlab.
    - Escreve uma string simples no PDF.
    - Chama a função load_docs para carregar o PDF.
    - Verifica se o retorno é uma lista (mesmo que o PDF tenha apenas uma página).
    """
    test_pdf = tmp_path / "test.pdf"  # Criando um PDF de teste no tmp_path
    c = canvas.Canvas(str(test_pdf))
    c.drawString(
        100,
        750,
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit. "
        "Donec molestie, ex id auctor aliquet, quam erat laoreet nibh, eu ultricies neque nibh et purus. "
        "Quisque in nisl non metus convallis aliquam vel id lacus. "
        "Nam felis felis, cursus eget commodo id, posuere sed nulla. "
        "Cras malesuada condimentum lacus, quis condimentum nisl vehicula sed."
        "Duis condimentum sodales sapien, eu rutrum dolor rhoncus eget. "
        "Quisque accumsan id quam et sagittis. Aliquam faucibus orci et orci faucibus ultricies.",
    )
    c.save()
    pages = load_docs(
        test_pdf
    )  # A função deve rodar sem erro, mesmo que o PDF esteja vazio
    assert isinstance(pages, list)


def test_create_vector_store_file_not_found(tmp_path, caplog):
    """
    Testa se create_vector_store lida corretamente com arquivo inexistente.
    """
    fake_pdf = tmp_path / "nao_existe.pdf"
    with caplog.at_level(logging.ERROR):
        create_vector_store(fake_pdf)
        assert "não foi encontrado" in caplog.text


def test_split_chunks_small_text():
    """
    Testa split_chunks com texto menor que o chunk_size.
    """
    from langchain.schema import Document

    pages = [Document(page_content="Pequeno texto.")]
    chunks = split_chunks(pages, "fake.pdf")
    assert len(chunks) == 1
    assert chunks[0].page_content == "Pequeno texto."


def test_create_embeddings_invalid_model(monkeypatch):
    """
    Testa se create_embeddings lança ValueError ao receber um modelo inválido.
    """
    monkeypatch.setenv("EMBEDDINGS_MODEL", "modelo-invalido")
    with pytest.raises(ValueError) as excinfo:
        create_embeddings()
    assert "Não foi possível carregar o modelo de embeddings" in str(excinfo.value)
