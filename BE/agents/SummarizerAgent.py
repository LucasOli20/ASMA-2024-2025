from spade import agent
from behaviours.summarize_memory import SummarizeMemoryBehaviour

class SummarizerAgent(agent.Agent):
    async def setup(self):
        print(f"[SummarizerAgent] Agent {str(self.jid)} iniciado.")
        self.add_behaviour(SummarizeMemoryBehaviour())
