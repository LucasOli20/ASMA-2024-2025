from spade.behaviour import CyclicBehaviour

class ReceiveFeedbackBehaviour(CyclicBehaviour):
    async def run(self):
        msg = await self.receive(timeout=10)
        if msg and msg.get_metadata("purpose") == "user_feedback":
            print(f"[FeedbackAgent] Feedback do utilizador recebido: {msg.body}")
