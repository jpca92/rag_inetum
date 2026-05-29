import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

from app.config import settings


class HuggingFaceLocalLLM:
    def __init__(self, model_name: str):
        self.model_name = model_name

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
        )

        dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            torch_dtype=dtype,
            device_map="auto" if torch.cuda.is_available() else None,
            trust_remote_code=True,
        )

        self.generator = pipeline(
            task="text-generation",
            model=self.model,
            tokenizer=self.tokenizer,
        )

    def generate_answer(self, question: str, context: str, history: str = "") -> str:
        prompt = self._build_prompt(
            question=question,
            context=context,
            history=history,
        )

        result = self.generator(
            prompt,
            max_new_tokens=settings.MAX_NEW_TOKENS,
            do_sample=settings.TEMPERATURE > 0,
            temperature=settings.TEMPERATURE,
            return_full_text=False,
        )

        return result[0]["generated_text"].strip()

    def _build_prompt(self, question: str, context: str, history: str) -> str:
        return f"""
Eres un asistente interno para consultas sobre información institucional de un banco.
Debes responder en español usando únicamente el contexto recuperado.
Si la respuesta no está en el contexto, indica que no tienes información suficiente.

Historial de conversación:
{history}

Contexto recuperado:
{context}

Pregunta:
{question}

Respuesta:
""".strip()