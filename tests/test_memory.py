from app.conversation.repository import ConversationRepository


def test_repository_saves_and_reads_messages(tmp_path):
    db_path = tmp_path / "test.db"
    repository = ConversationRepository(db_path=str(db_path))

    repository.save_message("s1", "user", "hola")
    repository.save_message("s1", "assistant", "hola, ¿cómo puedo ayudarte?")

    messages = repository.get_last_messages("s1", limit=2)

    assert len(messages) == 2
    assert messages[0]["role"] == "user"
    assert messages[1]["role"] == "assistant"