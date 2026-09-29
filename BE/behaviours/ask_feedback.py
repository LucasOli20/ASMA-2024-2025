from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

class AskFeedbackBehaviour(CyclicBehaviour):
    def __init__(self):
        super().__init__()
        self.counter = 0 

    async def run(self):
        msg = await self.receive(timeout=10)
        if msg and msg.get_metadata("source") == "dialogue_manager" and msg.get_metadata("purpose") == "trigger_feedback":
            print("[FeedbackAgent] Trigger de feedback recebido.")
            self.counter += 1

            # Enviar feedback apenas a cada 2 mensagens
            if self.counter % 2 != 0:
                print(f"[FeedbackAgent] Ignorado (contador = {self.counter}).")
                return

            memory_id = msg.get_metadata("memory_id")
            if not memory_id:
                print("[FeedbackAgent] ID de memória não encontrado.")
                return

            ask = Message(to=self.agent.get("dialogue_contact"))
            ask.set_metadata("performative", "inform")
            ask.set_metadata("source", "feedback_agent")
            ask.set_metadata("purpose", "ask_feedback")
            ask.body = "[FEEDBACK] " + json.dumps({
                "text": "Esta resposta foi útil?",
                "memory_id": memory_id
            })

            await self.send(ask)
            print(f"[FeedbackAgent] Pedido de feedback enviado (contador = {self.counter}).")
