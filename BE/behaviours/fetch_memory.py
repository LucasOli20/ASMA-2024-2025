import time
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from db.db import database
import jsonpickle

class FetchMemoryBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print("[MemoryAgent] Pedido para enviar toda a memória.")
            purpose = msg.get_metadata("purpose")
            try:
                if msg.get_metadata("performative") == "request":
                    if purpose == "emotion_request":
                        records = await database.fetch_all("SELECT text, response, subject, emotion FROM memory_messages")

                        # Verifica se todos os registos têm os campos obrigatórios preenchidos
                        invalid = any(record["text"] is None or record["text"].strip() == "" or
                                    record["response"] is None or record["response"].strip() == ""
                                    for record in records)

                        if invalid:
                            time.sleep(0.5)
                            records = await database.fetch_all("SELECT text, response, subject, emotion FROM memory_messages")

                        # Agora cria uma lista de dicionários
                        memories = [{"text": record["text"],"response": record["response"] ,"emotion": record["emotion"], "subject":record["subject"]} for record in records]

                        # Encode corretamente para enviar como mensagem
                        memory_message = Message(to=self.agent.get("dialogue_contact"))
                        memory_message.set_metadata("performative", "inform")
                        memory_message.set_metadata("source", "memory_agent")
                        memory_message.set_metadata("purpose", "full_memory")
                        memory_message.body = jsonpickle.encode(memories) 
                        await self.send(memory_message)

                        print("[MemoryAgent] Memória enviada ao DialogueManager.")
                    elif purpose == "memory_by_id":
                        content = jsonpickle.decode(msg.body)
                        memory_id = content.get("memory_id")

                        query = "SELECT * FROM memory_messages WHERE id = :memory_id"
                        record = await database.fetch_one(query=query, values={"memory_id": memory_id})

                        if record:
                            memory_entry = dict(record)
                            response_msg = Message(to=self.agent.get("dialogue_contact"))
                            response_msg.set_metadata("performative", "inform")
                            response_msg.set_metadata("source", "memory_agent")
                            response_msg.set_metadata("purpose", "memory_id_response")
                            response_msg.body = jsonpickle.encode(memory_entry)
                            await self.send(response_msg)
                            print(f"[MemoryAgent] Entrada {memory_id} enviada ao DialogueManager.")
                        else:
                            print(f"[MemoryAgent] Nenhuma entrada encontrada com ID={memory_id}.")
            except Exception as e:
                print(f"[MemoryAgent] Erro ao buscar memória: {e}")
