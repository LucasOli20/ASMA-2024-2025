from spade.agent import Agent
from behaviours.analyse_emotion import AnalyseEmotionBehaviour

class EmotionAgent(Agent):
    async def setup(self):
        print(f"[EmotionAgent] Agent {str(self.jid)} started.")
        self.add_behaviour(AnalyseEmotionBehaviour())
