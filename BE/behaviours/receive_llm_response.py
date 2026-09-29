from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
import asyncio
import json

class ReceiveLLMResponseBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            source = msg.get_metadata("source")
            try:
                sse_clients = self.agent.app.state.sse_clients
                if source == "dialogue_manager":
                    response = jsonpickle.decode(msg.body)

                    # 🚨 Garantir que é string
                    if isinstance(response.text, dict):
                        text = json.dumps(response.text, ensure_ascii=False, indent=2)
                    else:
                        text = response.text

                    for line in text.splitlines():
                        if line.strip():
                            for queue in sse_clients:
                                await queue.put(line)
                            await asyncio.sleep(0.1)

                elif source == "feedback_agent":
                    feedback_text = msg.body  # texto simples
                    for queue in sse_clients:
                        await queue.put(feedback_text)
                else:
                    print(f"[ReceiveLLMResponse] Fonte desconhecida: {source}")
            except Exception as e:
                print(f"[SSE] Erro ao enviar mensagem para clientes: {e}", flush=True)
