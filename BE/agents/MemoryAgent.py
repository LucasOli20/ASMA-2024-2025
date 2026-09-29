from spade import agent
from behaviours.update_memory import UpdateMemoryBehaviour
from behaviours.save_memory import SaveMemoryBehaviour
from behaviours.fetch_memory import FetchMemoryBehaviour

class MemoryAgent(agent.Agent):
    async def setup(self):
        print(f"[MemoryAgent] Agent {str(self.jid)} iniciado.")
        self.add_behaviour(SaveMemoryBehaviour())
        self.add_behaviour(FetchMemoryBehaviour())
        self.add_behaviour(UpdateMemoryBehaviour())

