from app.patterns.facade import RAGFacade


class FakeDoc:
    def __init__(self):
        self.page_content = "Contenido de prueba"
        self.metadata = {
            "title": "Título",
            "url": "https://example.com",
        }


def test_format_sources():
    facade = RAGFacade(
        retriever=None,
        llm_client=None,
        repository=None,
    )

    sources = facade._format_sources([FakeDoc()])

    assert sources[0]["title"] == "Título"
    assert sources[0]["url"] == "https://example.com"