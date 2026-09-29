from spade.behaviour import CyclicBehaviour
from spade.message import Message
import jsonpickle
from google.cloud import language_v1

client = language_v1.LanguageServiceClient()

class AnalyseEmotionBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)  
        if msg:
            print("[EmotionAgent] Mensagem recebida para análise emocional.")

            # Decode
            user_message = jsonpickle.decode(msg.body)

            try:
                document = language_v1.Document(content=user_message.text, type_=language_v1.Document.Type.PLAIN_TEXT)
                sentiment = client.analyze_sentiment(request={"document": document}).document_sentiment

                print(f"[EmotionAgent] Score de sentimento: {sentiment.score}, Magnitude: {sentiment.magnitude}")

                # Mapeamento melhorado
                if sentiment.score >= 0.6:
                    emotion = "very_happy"
                elif 0.2 <= sentiment.score < 0.6:
                    emotion = "happy"
                elif -0.2 < sentiment.score < 0.2:
                    if sentiment.magnitude > 1.0:
                        emotion = "mixed"
                    else:
                        emotion = "neutral"
                elif -0.6 <= sentiment.score <= -0.2:
                    emotion = "sad"
                else:  # sentiment.score < -0.6
                    emotion = "very_sad"

            except Exception as e:
                print(f"[EmotionAgent] Erro na análise de emoção: {e}")
                emotion = "neutral"

            user_message.emotion = emotion

            # Enviar de volta ao DialogueManager
            reply = Message(to=self.agent.get("dialogue_contact"))
            reply.set_metadata("performative", "inform")
            reply.set_metadata("source", "emotion_agent")
            reply.body = jsonpickle.encode(user_message)

            await self.send(reply)
            print(f"[EmotionAgent] Emoção detectada: {emotion}.")
