from .runnables import Runnable

class StrOutputParser(Runnable):
    def invoke(self, input):
        return str(input)
