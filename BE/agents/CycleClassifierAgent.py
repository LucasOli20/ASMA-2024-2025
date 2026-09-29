from spade.agent import Agent
from behaviours.classify_cycle import ClassifyCycleBehaviour

class CycleClassifierAgent(Agent):
    async def setup(self):
        print("[CycleClassifierAgent] Iniciar setup...")
        self.add_behaviour(ClassifyCycleBehaviour())
