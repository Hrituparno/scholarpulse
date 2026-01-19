def parse_paper(paper: dict) -> dict:
    """Lightweight parser that normalizes a paper dict.

    Expects keys like `title`, `authors`, `summary`, `pdf_url` and returns a
    cleaned dictionary suitable for other components.
    """
    return {
        "title": paper.get("title", "Untitled").strip(),
        "authors": paper.get("authors", []),
        "summary": (paper.get("summary") or "").strip(),
        "pdf_url": paper.get("pdf_url"),
    }
