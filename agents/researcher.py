from agent.lit_review import LiteratureReviewer


class ResearchAgent:
    """Reads papers and provides structured results."""

    def __init__(self):
        self.reviewer = LiteratureReviewer()

    def fetch_papers(self, query: str, max_results: int = 5):
        return self.reviewer.search(query, max_results=max_results)
