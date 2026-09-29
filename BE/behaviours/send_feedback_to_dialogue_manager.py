# behaviours/send_feedback_to_dialogue_manager.py

from spade.behaviour import OneShotBehaviour
from spade.message import Message
import jsonpickle

class SendFeedbackToDialogueManagerBehaviour(OneShotBehaviour):
    def __init__(self, dialogue_jid: str, memory_id: int, feedback: str, suggestion: str):
        super().__init__()
        self.dialogue_jid = dialogue_jid
        self.memory_id = memory_id
        self.feedback = feedback
        self.suggestion = suggestion

    async def run(self):
        feedback_msg = Message(to=self.dialogue_jid)
        feedback_msg.set_metadata("performative", "inform")
        feedback_msg.set_metadata("source", "fastapi_server")
        feedback_msg.set_metadata("purpose", "feedback_update")

        body = {
            "memory_id": self.memory_id,
            "feedback": self.feedback,
            "suggestion": self.suggestion,
        }
        feedback_msg.body = jsonpickle.encode(body)

        await self.send(feedback_msg)
        print("[SendFeedbackToDialogueManagerBehaviour] Feedback enviado para DialogueManagerAgent.")
