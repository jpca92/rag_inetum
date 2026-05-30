import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

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

    def generate_answer(self, question: str, context: str, history: str = "") -> str:
        messages = [
            {
                "role": "system",
                "content": (
                    "Eres un asistente interno especializado en responder preguntas "
                    "sobre información institucional de un banco. "
                    "Responde siempre en español. "
                    "Usa únicamente el contexto recuperado. "
                    "No inventes información. "
                    "No repitas frases. "
                    "No escribas 'respuesta correcta' ni 'respuesta incorrecta'. "
                    "No generes preguntas adicionales. "
                    "Responde de forma breve, clara y profesional. "
                    "Si no hay información suficiente en el contexto, di: "
                    "'No tengo información suficiente en los documentos recuperados para responder eso.'"
                ),
            },
            {
                "role": "user",
                "content": self._build_user_prompt(
                    question=question,
                    context=context,
                    history=history,
                ),
            },
        ]

        prompt = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            truncation=True,
            max_length=4096,
        )

        if torch.cuda.is_available():
            inputs = {key: value.to(self.model.device) for key, value in inputs.items()}

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=settings.MAX_NEW_TOKENS,
                do_sample=False,
                repetition_penalty=1.15,
                no_repeat_ngram_size=4,
                eos_token_id=self.tokenizer.eos_token_id,
                pad_token_id=self.tokenizer.eos_token_id,
            )

        generated_tokens = outputs[0][inputs["input_ids"].shape[-1]:]
        answer = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        )

        return self._postprocess_answer(answer)

    def _build_user_prompt(self, question: str, context: str, history: str) -> str:
        return f"""
Historial reciente de la conversación:
{history}

Contexto recuperado desde la base vectorial:
{context}

Pregunta del usuario:
{question}

Instrucciones de respuesta:
- Responde solo la pregunta del usuario.
- No repitas listas.
- No agregues preguntas inventadas.
- No incluyas frases como "respuesta correcta" o "respuesta incorrecta".
- Si mencionas productos, organízalos en viñetas.
- Si el contexto no contiene la respuesta, dilo claramente.

Respuesta:
""".strip()

    def _postprocess_answer(self, answer: str) -> str:
        stop_phrases = [
            "Pregunta del usuario:",
            "Contexto recuperado",
            "Respuesta incorrecta",
            "La respuesta correcta es",
            "Haz una pregunta",
        ]

        for phrase in stop_phrases:
            if phrase in answer:
                answer = answer.split(phrase)[0]

        lines = []
        seen = set()

        for line in answer.splitlines():
            clean_line = line.strip()

            if not clean_line:
                continue

            if clean_line.lower() in seen:
                continue

            seen.add(clean_line.lower())
            lines.append(clean_line)

        return "\n".join(lines).strip()