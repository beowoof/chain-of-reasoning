class Runnable:
    """Minimal runnable base class used for testing."""
    def invoke(self, input):
        raise NotImplementedError
    def __or__(self, other):
        return RunnableSequence([self, other])

class RunnableSequence(Runnable):
    def __init__(self, runnables):
        self._runnables = runnables
    def __or__(self, other):
        return RunnableSequence(self._runnables + [other])
    def invoke(self, input):
        result = input
        for runnable in self._runnables:
            result = runnable.invoke(result)
        return result
