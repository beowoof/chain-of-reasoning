from langchain_core.runnables import Runnable

class BaseTool(Runnable):
    name: str = ""
    description: str = ""
    def _run(self, query: str) -> str:
        raise NotImplementedError
    def invoke(self, input):
        return self._run(input)
