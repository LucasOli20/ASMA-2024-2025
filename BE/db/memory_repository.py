from db.db import database
from db.models import memory

# Guardar uma nova entrada de memória
async def save_memory(text: str, emotion: str = None, response: str = None, feedback: str = None):
    query = memory.insert().values(
        text=text,
        emotion=emotion,
        response=response,
        feedback=feedback
    ).returning(memory.c.id)
    inserted_id = await database.execute(query)
    return inserted_id

# Atualizar campos de uma memória existente (pelo ID)
async def update_memory(memory_id: int, feedback: str, suggestion: str | None = None):
    query = """
    UPDATE memory_messages
    SET feedback = :feedback, user_suggestion = :suggestion
    WHERE id = :memory_id
    """
    values = {"feedback": feedback, "suggestion": suggestion, "memory_id": memory_id}
    await database.execute(query=query, values=values)

