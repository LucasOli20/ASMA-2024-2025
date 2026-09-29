from spade import agent
from behaviours.call_gemini_response import CallGeminiBehaviour

class LLMAgent(agent.Agent):
    async def setup(self):
        self.add_behaviour(CallGeminiBehaviour())
