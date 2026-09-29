from spade import agent
from behaviours.receive_user_input import ReceiveUserInputBehaviour
from behaviours.receive_llm_response import ReceiveLLMResponseBehaviour

class UserInterfaceAgent(agent.Agent):
    def __init__(self, jid, password, app=None):
        super().__init__(jid, password)
        self.app = app

    async def setup(self):
        self.add_behaviour(ReceiveLLMResponseBehaviour())

    def create_send_behaviour(self, message_text, message_subject):
        return ReceiveUserInputBehaviour(message_text, message_subject)
