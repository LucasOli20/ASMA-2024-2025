from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
from db.db import database
import os

class SaveMemoryBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            if msg.get_metadata("purpose") != "save_memory":
                return

            print("[MemoryAgent] Mensagem recebida para guardar memória.")

            try:
                user_message = jsonpickle.decode(msg.body)

                query = """
                INSERT INTO memory_messages (text, emotion, subject) 
                VALUES (:text, :emotion, :subject) 
                RETURNING id;
                """
                values = {
                    "text": user_message.text,
                    "emotion": getattr(user_message, "emotion", None),
                    "subject" : getattr(user_message, "subject", None)
                }
                inserted_id = await database.execute(query=query, values=values)

                print(f"[MemoryAgent] Memória guardada na base de dados: {user_message.text} (ID {inserted_id})")

                reply = Message(to=self.agent.get("dialogue_contact"))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("source", "memory_agent")
                reply.set_metadata("purpose", "save_memory")
                reply.body = jsonpickle.encode({"status": "saved", "memory_id": inserted_id})

                await self.send(reply)
                print("[MemoryAgent] Confirmação de memória guardada enviada ao DialogueManager.")

            except Exception as e:
                print(f"[MemoryAgent] Erro ao guardar memória: {e}")


