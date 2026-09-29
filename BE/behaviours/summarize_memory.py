from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
import google.generativeai as genai
import os

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.0-flash-lite")

class SummarizeMemoryBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            print("[SummarizerAgent] Memória recebida para reestruturar.")

            try:
                memory_messages = jsonpickle.decode(msg.body)
                # Criar histórico com perguntas e respostas
                memory_text = "\n\n".join([
                    f"[{m.get('subject', 'desconhecido')}]\n"
                    f"Utilizador: {m['text']}\nAssistente: {m['response']}"
                    for m in memory_messages if m.get('text') and m.get('response')
                ]).strip()

                if not memory_text:
                    print("[SummarizerAgent] Memória vazia. Nada para processar.")
                    history = ""
                else:
                    prompt = (
                        "Tens abaixo o histórico de uma conversa entre um utilizador e um assistente virtual.\n"
                        "Reestrutura o conteúdo de forma clara, organizada e fiel, mantendo todas as interações.\n"
                        "Não resumas, apenas reescreve com formatação limpa e lógica para que outro modelo perceba o que foi dito até agora.\n"
                        "⚠️ É muito importante que mantenhas o **assunto (subject)** de cada interação visível no texto, tal como aparece no original.\n"
                        "Exemplo:\n"
                        "[matemática]\nUtilizador: ...\nAssistente: ...\n\n[história]\nUtilizador: ...\nAssistente: ...\n\n"
                        "Mantém sempre essa estrutura com o assunto entre parêntesis retos antes de cada par de mensagens.\n\n"
                        "**IMPORTANTE**"
                        "   - Se o histórico estiver vazio ou não houver interações relevantes com esse tema, responde apenas com \"\" (duas aspas).\n\n"
                        f"{memory_text}"
                    )

                    response = model.generate_content(prompt)
                    history = response.text if response.text else "Histórico indisponível."
                    
                    print(f"[SummarizerAgent] Histórico reestruturado gerado.")

                # Enviar histórico reestruturado
                reply = Message(to=self.agent.get("dialogue_contact"))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("source", "summarizer_agent")
                reply.body = history

                await self.send(reply)
                print("[SummarizerAgent] Histórico enviado ao DialogueManager.")

            except Exception as e:
                print(f"[SummarizerAgent] Erro ao reestruturar memória: {e}")
