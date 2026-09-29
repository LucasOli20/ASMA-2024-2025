# behaviours/update_memory.py

from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
from db.db import database

class UpdateMemoryBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print("[MemoryAgent] Pedido de atualização da memória recebido.")
            if msg.get_metadata("purpose") != "update_memory":
                return
            try:
                data = jsonpickle.decode(msg.body)
                memory_id = data.get("memory_id")
                update_fields = data.get("update_fields", {})
                
                if not memory_id or not update_fields:
                    print("[MemoryAgent] Dados inválidos para update.")
                    return

                # Substituir dict por full_answer se o campo for 'text'
                update_values = {}
                for key, val in update_fields.items():
                    if key == "response" and isinstance(val, dict):
                        update_values[key] = val.get("full_answer", "[resposta indisponível]")
                    else:
                        update_values[key] = val
                update_values["memory_id"] = memory_id

                # Gerar set_clause com base em update_values (e não em update_fields diretamente!)
                set_clause = ", ".join([f"{field} = :{field}" for field in update_values if field != "memory_id"])
                query = f"UPDATE memory_messages SET {set_clause} WHERE id = :memory_id;"

                await database.execute(query=query, values=update_values)

                print(f"[MemoryAgent] Memória ID {memory_id} atualizada: {update_values}")

                reply = Message(to=self.agent.get("dialogue_contact"))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("source", "memory_agent")
                reply.body = jsonpickle.encode({"status": "updated", "memory_id": memory_id})

                await self.send(reply)

            except Exception as e:
                print(f"[MemoryAgent] Erro ao atualizar memória: {e}")
