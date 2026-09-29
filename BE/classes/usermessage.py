class UserMessage:
    def __init__(self, sender, text, emotion=None, subject="História"):
        self.sender = sender
        self.text = text
        self.emotion = emotion
        self.subject = subject
