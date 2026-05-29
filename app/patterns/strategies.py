from abc import ABC, abstractmethod
import re


class CleaningStrategy(ABC):
    @abstractmethod
    def clean(self, text: str) -> str:
        raise NotImplementedError


class BasicCleaningStrategy(CleaningStrategy):
    def clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)
        return text.strip()


class BankingWebsiteCleaningStrategy(CleaningStrategy):
    def clean(self, text: str) -> str:
        text = re.sub(r"\s+", " ", text)

        repeated_fragments = [
            "Hazlo en BBVA",
            "Personas Empresas",
            "Ir al contenido principal",
            "Buscar",
            "Cerrar",
            "Menú",
            "Cookies",
        ]

        for fragment in repeated_fragments:
            text = text.replace(fragment, " ")

        text = re.sub(r"\s+", " ", text)

        return text.strip()