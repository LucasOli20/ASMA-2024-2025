from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
import google.generativeai as genai
import os

# Configurar o modelo da Google Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

class ClassifyCycleBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)  # Espera por mensagem
        if msg:
            print("[CycleClassifierAgent] Mensagem recebida para classificar ciclo.")
            performative = msg.get_metadata("performative")
            source = msg.get_metadata("source")

            if performative == "inform":
                try:
                    user_message = jsonpickle.decode(msg.body)

                    question = user_message.text

                    # Criar o prompt especial para classificar o ciclo
                    prompt = (
                        "A seguinte pergunta pertence a que ciclo escolar em Portugal?\n\n"
                        f"Pergunta: {question}\n\n"
                        "Responde apenas com: '1º ciclo', '2º ciclo' ou '3º ciclo'."
                    )

                    response = model.generate_content(prompt)
                    detected_cycle = response.text.strip()

                    if detected_cycle not in ["1º ciclo", "2º ciclo", "3º ciclo"]:
                        print("[CycleClassifierAgent] Resposta inválida recebida. Assumindo '3º ciclo'.")
                        detected_cycle = "3º ciclo"

                except Exception as e:
                    print(f"[CycleClassifierAgent] Erro a classificar ciclo: {e}")
                    detected_cycle = "3º ciclo"

                # Enviar resposta de volta para o DialogueManagerAgent
                reply = Message(to=self.agent.get("dialogue_contact"))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("source", "cycle_classifier_agent")
                reply.body = jsonpickle.encode({"cycle": detected_cycle})

                await self.send(reply)
                print(f"[CycleClassifierAgent] Ciclo classificado e enviado: {detected_cycle}")
