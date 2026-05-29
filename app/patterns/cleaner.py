from app.patterns.strategies import (
    BankingWebsiteCleaningStrategy,
    CleaningStrategy,
)


class TextCleaner:
    def __init__(self, strategy: CleaningStrategy | None = None):
        self.strategy = strategy or BankingWebsiteCleaningStrategy()

    def clean(self, text: str) -> str:
        return self.strategy.clean(text)