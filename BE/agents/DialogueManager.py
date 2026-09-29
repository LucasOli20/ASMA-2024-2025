from spade import agent
from behaviours.process_dialogue import ProcessDialogueBehaviour

class DialogueManagerAgent(agent.Agent):
    async def setup(self):
        self.add_behaviour(ProcessDialogueBehaviour())
