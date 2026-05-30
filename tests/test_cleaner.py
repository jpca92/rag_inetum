from app.patterns.strategies import BasicCleaningStrategy
from app.scraping.cleaner import TextCleaner


def test_cleaner_removes_extra_spaces():
    cleaner = TextCleaner(strategy=BasicCleaningStrategy())

    result = cleaner.clean(" Hola     mundo \n desde   RAG ")

    assert result == "Hola mundo desde RAG"