class FAISS:
    def __init__(self):
        self.docs = []
    @classmethod
    def from_documents(cls, documents, embedding):
        obj = cls()
        obj.docs.extend(documents)
        return obj
    @classmethod
    def load_local(cls, path, embeddings, allow_dangerous_deserialization=False):
        return cls()
    def add_documents(self, docs):
        self.docs.extend(docs)
    def as_retriever(self, search_kwargs=None):
        class Retriever:
            def __init__(self, docs):
                self.docs = docs
            def invoke(self, query):
                return self.docs
        return Retriever(self.docs)
    def save_local(self, path):
        pass
