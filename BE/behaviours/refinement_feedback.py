from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle

class RefinementBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg and msg.get_metadata("source") == "dialogue_manager" and msg.get_metadata("performative") == "inform":

            purpose = msg.get_metadata("purpose")
    
            # Passo 1 – Recebe o pedido de refinamento
            if purpose == "refine_response":
                print("[RefinementBehaviour] Pedido de refinamento recebido.")
                content = jsonpickle.decode(msg.body)
                memory_id = content.get("memory_id")
                feedback = content.get("feedback")
                suggestion = content.get("user_suggestion")

                # Guardar no estado do behaviour se necessário
                self.agent.temp_feedback = {
                    "memory_id": memory_id,
                    "user_suggestion": suggestion
                }

                # Pedir todos os campos ao MemoryAgent
                request_msg = Message(to=self.agent.get("dialogue_contact"))
                request_msg.set_metadata("performative", "request")
                request_msg.set_metadata("source", "feedback_agent")
                request_msg.set_metadata("purpose", "memory_by_id")

                request_msg.body = jsonpickle.encode({"memory_id": memory_id})
                await self.send(request_msg)
                print(f"[RefinementBehaviour] Pedido completo de memória enviado ao MemoryAgent (ID={memory_id}).")

            elif purpose == "memory_id_response":
                print("[RefinementBehaviour] Dados completos recebidos do MemoryAgent.")
                memory_entry = jsonpickle.decode(msg.body)

                text = memory_entry.get("text", "")
                previous_response = memory_entry.get("response", "")
                emotion = memory_entry.get("emotion", "")
                cycle = memory_entry.get("cycle", "")
                feedback = memory_entry.get("feedback", "")
                suggestion =  memory_entry.get("user_suggestion")

                if feedback == "not_useful":
                    # Criar prompt refinado
                    refined_prompt = (
                        f"Estás a atuar como **MentorAI**, um professor de História do {cycle} em Portugal, que responde a alunos de forma clara, empática e educativa.\n\n"

                        "⛔ A tua resposta anterior não foi considerada útil pelo aluno. Segue abaixo o que aconteceu:\n\n"
                        f"📨 Pergunta original do aluno:\n{text}\n\n"
                        f"🤖 Tua resposta anterior:\n{previous_response}\n\n"
                        "🛑 Feedback do aluno: considerou a resposta 'não útil'.\n"
                        f"📝 Sugestão do aluno para melhorar a resposta: {suggestion}\n\n"

                        "🚀 **A tua tarefa agora é muito clara:**\n"
                        "- Reescreve completamente a resposta ao aluno, com base na pergunta original, na tua resposta anterior, e na sugestão que o aluno deu.\n"
                        "- Evita repetir os mesmos erros da resposta anterior.\n"
                        "- Incorpora o conteúdo ou estilo sugerido pelo aluno, se for adequado.\n"
                        "- Usa um tom educativo, ajustado ao ciclo indicado.\n"
                        "- **Não te apresentes de novo. Não digas 'Olá' nem 'Sou o MentorAI'. Já estás a meio de uma conversa.**\n"
                        "- Considera também o estado emocional do aluno: '{emotion}'. Se ele estiver frustrado, responde com mais paciência e empatia.\n"
                        "- Escreve em português de Portugal.\n\n"

                        "✏️ Gera agora uma nova resposta, melhorada e orientada para esclarecer a dúvida do aluno com qualidade pedagógica."
                    )

                    print("[RefinementBehaviour] Prompt refinado criado. Enviando ao DialogueManager...")

                    # Enviar prompt ao DialogueManager
                    fwd_msg = Message(to=self.agent.get("dialogue_contact"))
                    fwd_msg.set_metadata("performative", "inform")
                    fwd_msg.set_metadata("source", "feedback_agent")
                    fwd_msg.set_metadata("purpose", "regenerate_response_prompt")
                    fwd_msg.body = jsonpickle.encode({"prompt": refined_prompt})

                    await self.send(fwd_msg)
                else:
                    print("[RefinementBehaviour] Feedback não é 'not_useful'. Nenhuma ação de refinamento será feita.")

