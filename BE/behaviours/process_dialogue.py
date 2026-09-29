import time
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle


class ProcessDialogueBehaviour(CyclicBehaviour):
    
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg:
            performative = msg.get_metadata("performative")
            source = msg.get_metadata("source")

            if performative == "request" and source == "userInterface_agent":
                print("[DialogueManager] Recebida pergunta. Encaminhar para EmotionAgent.")
                fwd = Message(to=self.agent.get("emotion_contact"))
                fwd.set_metadata("performative", "inform")
                fwd.body = msg.body
                await self.send(fwd)

                user_message = jsonpickle.decode(msg.body)
                self.agent.set("current_subject", user_message.subject)

                # Encaminhar para o CycleClassifierAgent
                cycle_msg = Message(to=self.agent.get("cycle_classifier_contact"))
                cycle_msg.set_metadata("performative", "inform")
                cycle_msg.body = msg.body
                await self.send(cycle_msg)
            
            elif performative == "inform" and source == "cycle_classifier_agent":
                classification = jsonpickle.decode(msg.body)
                detected_cycle = classification.get("cycle")
                print(f"[DialogueManager] Ciclo recebido: {detected_cycle}")

                self.agent.set("current_cycle", detected_cycle)

            elif performative == "inform" and source == "emotion_agent":
                print("[DialogueManager] Emoção analisada.")

                request_memory = Message(to=self.agent.get("memory_contact"))
                request_memory.set_metadata("performative", "request")
                request_memory.set_metadata("purpose", "emotion_request")

                await self.send(request_memory)
                print("[DialogueManager] Pedido de memória enviado ao MemoryAgent.")

                user_message = jsonpickle.decode(msg.body)
                user_message.subject = self.agent.get("current_subject")

                save_memory = Message(to=self.agent.get("memory_contact"))
                save_memory.set_metadata("performative", "inform")
                save_memory.set_metadata("purpose", "save_memory")
                save_memory.body = jsonpickle.encode(user_message)
                await self.send(save_memory)
                print("[DialogueManager] Nova memória enviada para MemoryAgent.")

                self.agent.set("current_user_message", jsonpickle.decode(msg.body))

            elif performative == "inform" and source == "memory_agent":
                purpose = msg.get_metadata("purpose")

                if purpose == "full_memory":
                    print("[DialogueManager] Memória recebida. Encaminhar para SummarizerAgent.")
                    fwd = Message(to=self.agent.get("summarizer_contact"))
                    fwd.set_metadata("performative", "inform")
                    fwd.set_metadata("source", "dialogue_manager")
                    fwd.body = msg.body
                    await self.send(fwd)

                elif purpose == "save_memory":
                    confirmation = jsonpickle.decode(msg.body)
                    if confirmation.get("status") == "saved":
                        memory_id = confirmation.get("memory_id")
                        self.agent.set("current_memory_id", memory_id)
                        print(f"[DialogueManager] Memória guardada com ID {memory_id} (guardado no estado).")

                elif purpose == "update_memory":
                    confirmation = jsonpickle.decode(msg.body)
                    if confirmation.get("status") == "updated":
                        memory_id = confirmation.get("memory_id")
                        print(f"[DialogueManager] Memória ID {memory_id} atualizada com sucesso.")
                elif purpose == "memory_id_response":
                    print("[DialogueManager] Memória por ID recebida do MemoryAgent. Encaminhar para FeedbackAgent.")

                    fwd = Message(to=self.agent.get("feedback_contact"))
                    fwd.set_metadata("performative", "inform")
                    fwd.set_metadata("source", "dialogue_manager")
                    fwd.set_metadata("purpose", "memory_id_response")
                    fwd.body = msg.body

                    await self.send(fwd)
                else:
                    print("[DialogueManager] Confirmação de memória guardada recebida, sem ID.")
                        
            elif performative == "inform" and source == "summarizer_agent":
                print("[DialogueManager] Resumo recebido. Agora preparar mensagem para LLMAgent...")

                # Preparar mensagem composta para o LLM
                composed_data = {
                    "summary": msg.body,
                    "user_message": self.agent.get("current_user_message"),
                    "cycle": self.agent.get("current_cycle"),
                    "subject": self.agent.get("current_subject")
                }

                llm_message = Message(to=self.agent.get("llm_contact"))
                llm_message.set_metadata("performative", "inform")
                llm_message.set_metadata("source", "dialogue_manager")
                llm_message.set_metadata("purpose", "final_prompt")
                llm_message.body = jsonpickle.encode(composed_data)

                await self.send(llm_message)
                print("[DialogueManager] Informação enviada ao LLMAgent.")

            elif performative == "inform" and source == "llm_agent":
                print("[DialogueManager] Resposta do LLM recebida. Enviar para UserInterface.")
                reply = Message(to=self.agent.get("user_interface_contact"))
                reply.set_metadata("performative", "inform")
                reply.set_metadata("source", "dialogue_manager")
                reply.body = msg.body
                await self.send(reply)
                print("[DialogueManager] Resposta enviada ao utilizador.")

                llm_response = jsonpickle.decode(msg.body)

                update_msg= Message(to=self.agent.get("memory_contact"))
                update_msg.set_metadata("performative", "inform")
                update_msg.set_metadata("source", "dialogue_manager")
                update_msg.set_metadata("purpose", "update_memory")

                memory_test = self.agent.get("current_memory_id")
                while memory_test is None:
                    time.sleep(0.6)
                    memory_test = self.agent.get("current_memory_id")
                print(f"current_memory_id {memory_test}")

                update_body = {
                    "memory_id": self.agent.get("current_memory_id"),
                    "update_fields": {
                        "response": llm_response.text,
                        "cycle": self.agent.get("current_cycle")
                    }
                }

                update_msg.body = jsonpickle.encode(update_body)
                await self.send(update_msg)

                # Enviar trigger ao FeedbackAgent
                feedback_trigger = Message(to=self.agent.get("feedback_contact"))
                feedback_trigger.set_metadata("performative", "inform")
                feedback_trigger.set_metadata("source", "dialogue_manager")
                feedback_trigger.set_metadata("purpose", "trigger_feedback")
                feedback_trigger.set_metadata("memory_id", str(self.agent.get("current_memory_id")))
                feedback_trigger.body = msg.body 
                await self.send(feedback_trigger)
                print("[DialogueManager] Trigger de feedback enviado ao FeedbackAgent.")

            elif performative == "inform" and source == "feedback_agent":
                purpose = msg.get_metadata("purpose")
                if purpose == "ask_feedback":
                    print("[DialogueManager] Mensagem de feedback recebida. Enviar ao utilizador.")
                    feedback_question = Message(to=self.agent.get("user_interface_contact"))
                    feedback_question.set_metadata("performative", "inform")
                    feedback_question.set_metadata("source", "feedback_agent")
                    feedback_question.body = msg.body
                    await self.send(feedback_question)

                if purpose == "regenerate_response_prompt":
                    print("[DialogueManager] Prompt refinado recebido do FeedbackAgent. Reencaminhar para LLMAgent.")
                    llm_msg = Message(to=self.agent.get("llm_contact"))
                    llm_msg.set_metadata("performative", "inform")
                    llm_msg.set_metadata("source", "dialogue_manager")
                    llm_msg.set_metadata("purpose", "regenerate")

                    llm_msg.body = msg.body  # contém {"prompt": ..., "cycle": ...}
                    await self.send(llm_msg)
            
            elif performative == "request" and source == "feedback_agent":
                if msg.get_metadata("purpose") == "memory_by_id":
                    print("[DialogueManager] Pedido de memória recebido do FeedbackAgent.")
                    
                    request_memory = Message(to=self.agent.get("memory_contact"))
                    request_memory.set_metadata("performative", "request")
                    request_memory.set_metadata("source", "dialogue_manager")
                    request_memory.set_metadata("purpose", "memory_by_id")

                    request_memory.body = msg.body  # contém o memory_id
                    await self.send(request_memory)
                    print("[DialogueManager] Pedido de memória reencaminhado para o MemoryAgent.")


            elif performative == "inform" and source == "fastapi_server":
                if msg.get_metadata("purpose") == "feedback_update":
                    print("[DialogueManager] Pedido de update de feedback recebido.")

                    # Decodificar o feedback recebido
                    feedback_data = jsonpickle.decode(msg.body)
                    memory_id = feedback_data.get("memory_id")
                    feedback = feedback_data.get("feedback")
                    suggestion = feedback_data.get("suggestion")

                    # Criar mensagem para o MemoryAgent
                    memory_update = Message(to=self.agent.get("memory_contact"))
                    memory_update.set_metadata("performative", "inform")
                    memory_update.set_metadata("source", "dialogue_manager")
                    memory_update.set_metadata("purpose", "update_memory")
                    
                    update_body = {
                        "memory_id": memory_id,
                        "update_fields": {
                            "feedback": feedback,
                            "user_suggestion": suggestion
                        }
                    }
                    memory_update.body = jsonpickle.encode(update_body)

                    await self.send(memory_update)
                    print(f"[DialogueManager] Feedback enviado ao MemoryAgent para atualizar memória {memory_id}.")

                    # Criar mensagem para o FeedbackAgent com o propósito de refinar a resposta
                    refinement_msg = Message(to=self.agent.get("feedback_contact"))
                    refinement_msg.set_metadata("performative", "inform")
                    refinement_msg.set_metadata("source", "dialogue_manager")
                    refinement_msg.set_metadata("purpose", "refine_response")

                    refinement_payload = {
                        "memory_id": memory_id,
                        "feedback": feedback,
                        "user_suggestion": suggestion
                    }

                    refinement_msg.body = jsonpickle.encode(refinement_payload)

                    await self.send(refinement_msg)
                    print(f"[DialogueManager] Pedido de refinamento enviado ao FeedbackAgent com memória {memory_id}.")


            else:
                print(f"[DialogueManager] Mensagem recebida de {source} com performativa {performative}.")


