from langchain_core.runnables import Runnable

class OllamaLLM(Runnable):
    def __init__(self, model: str, temperature: float = 0.0):
        self.model = model
        self.temperature = temperature
    def invoke(self, input):
        return ""

class OllamaEmbeddings:
    def __init__(self, model: str):
        self.model = model
