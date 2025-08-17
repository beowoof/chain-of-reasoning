from .runnables import Runnable

class PromptTemplate(Runnable):
    def __init__(self, template: str):
        self.template = template
    @classmethod
    def from_template(cls, template: str):
        return cls(template)
    def invoke(self, inputs: dict) -> str:
        return self.template.format(**inputs)

class ChatPromptTemplate(PromptTemplate):
    pass
