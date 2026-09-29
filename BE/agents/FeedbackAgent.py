from spade.agent import Agent
from behaviours.refinement_feedback import RefinementBehaviour
from behaviours.ask_feedback import AskFeedbackBehaviour
from behaviours.receive_feedback import ReceiveFeedbackBehaviour

class FeedbackAgent(Agent):
    async def setup(self):
        print("[FeedbackAgent] Iniciado.")
        self.add_behaviour(AskFeedbackBehaviour())
        self.add_behaviour(ReceiveFeedbackBehaviour())
        self.add_behaviour(RefinementBehaviour())
