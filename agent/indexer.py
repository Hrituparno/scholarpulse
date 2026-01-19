from typing import List
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neighbors import NearestNeighbors
except Exception:
    TfidfVectorizer = None
    NearestNeighbors = None


class Indexer:
    """Simple optional indexer: uses TF-IDF + NearestNeighbors fallback.

    If `faiss` or LangChain/FAISS integrations are available you can replace
    this with a higher-performance implementation. This implementation keeps
    the dependency surface small and works offline.
    """

    def __init__(self):
        if TfidfVectorizer is None or NearestNeighbors is None:
            raise RuntimeError("scikit-learn is required for the indexing fallback. Install scikit-learn.")
        self.vectorizer = TfidfVectorizer(max_features=2048)
        self.nn = None
        self.docs = []

    def build(self, papers: List[dict]):
        texts = [p.get("summary", "") for p in papers]
        X = self.vectorizer.fit_transform(texts).toarray()
        self.nn = NearestNeighbors(n_neighbors=min(5, len(texts)), metric="cosine").fit(X)
        self.docs = papers
        self._X = X

    def query(self, query_text: str, k: int = 5):
        if not self.nn:
            return []
        v = self.vectorizer.transform([query_text]).toarray()
        dists, idx = self.nn.kneighbors(v, n_neighbors=min(k, len(self.docs)))
        return [self.docs[i] for i in idx[0]]
