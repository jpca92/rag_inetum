from app.config import settings
from app.conversation.repository import ConversationRepository


class ConversationMemory:
    def __init__(self, repository: ConversationRepository):
        self.repository = repository

    def get_formatted_history(self, session_id: str) -> str:
        messages = self.repository.get_last_messages(
            session_id=session_id,
            limit=settings.MEMORY_N_MESSAGES,
        )

        return "\n".join(
            f"{message['role']}: {message['content']}"
            for message in messages
        )