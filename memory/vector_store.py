from agent.indexer import Indexer


class VectorStore:
    """Simple wrapper around the TF-IDF indexer fallback.

    This provides the `memory/vector_store.py` expected by project layout.
    """

    def __init__(self):
        self.indexer = Indexer()

    def build(self, papers):
        self.indexer.build(papers)

    def query(self, text, k=5):
        return self.indexer.query(text, k=k)
