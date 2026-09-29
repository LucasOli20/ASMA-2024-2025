from spade.behaviour import OneShotBehaviour
from spade.message import Message
import jsonpickle
from classes.usermessage import UserMessage

class ReceiveUserInputBehaviour(OneShotBehaviour):
    def __init__(self, text, subject):
        super().__init__()
        self.text = text
        self.subject = subject

    async def run(self):
        msg = UserMessage(str(self.agent.jid), self.text, subject=self.subject)
        print(f"[UserInterface] Enviando: {msg.text}")

        message = Message(to=self.agent.get("dialogue_contact"))
        message.set_metadata("performative", "request")
        message.set_metadata("source", "userInterface_agent")
        message.body = jsonpickle.encode(msg)

        await self.send(message)
