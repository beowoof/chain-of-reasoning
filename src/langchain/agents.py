class AgentExecutor:
    def __init__(self, agent, tools, **kwargs):
        self.agent = agent
        self.tools = tools
    def invoke(self, *args, **kwargs):
        if hasattr(self.agent, 'invoke'):
            return self.agent.invoke(*args, **kwargs)
        return {}

def create_react_agent(llm, tools, prompt):
    class SimpleAgent:
        def invoke(self, inputs):
            return {}
    return SimpleAgent()
