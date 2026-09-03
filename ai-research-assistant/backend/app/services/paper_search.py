import requests


def get_authors(work):
    authors = []

    for author in work.get("authorships", []):
        author_info = author.get("author", {})

        name = author_info.get("display_name")

        if name:
            authors.append(name)

    return authors


def get_abstract(work):
    abstract_inverted_index = work.get("abstract_inverted_index")

    if not abstract_inverted_index:
        return None

    words = []

    for word, positions in abstract_inverted_index.items():

        for position in positions:
            words.append((position, word))

    words.sort()

    return " ".join(
        word for _, word in words
    )


def get_pdf_url(work):

    best_oa_location = work.get("best_oa_location")

    if not best_oa_location:
        return None

    return best_oa_location.get("pdf_url")


def get_topics(work):

    topics = []

    for topic in work.get("topics", []):

        display_name = topic.get("display_name")

        if display_name:
            topics.append(display_name)

    return topics


def format_paper(work):

    return {
        "id": work.get("id"),

        "title": work.get("title"),

        "publication_year": work.get(
            "publication_year"
        ),

        "publication_date": work.get(
            "publication_date"
        ),

        "doi": work.get("doi"),

        "authors": get_authors(work),

        "abstract": get_abstract(work),

        "journal": (
            (work.get("primary_location") or {})
            .get("source") or {}
        ).get("display_name") if work.get("primary_location") else None,

        "cited_by_count": work.get(
            "cited_by_count"
        ),

        "pdf_url": get_pdf_url(work),

        "topics": get_topics(work),

        "is_open_access": (
            work.get("open_access", {})
            .get("is_oa", False)
        )
    }


def search_papers(query: str, limit: int = 10):

    url = "https://api.openalex.org/works"

    params = {
        "search": query,
        "per-page": limit
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()

    papers = []

    for work in data.get("results", []):

        papers.append(
            format_paper(work)
        )

    return papers