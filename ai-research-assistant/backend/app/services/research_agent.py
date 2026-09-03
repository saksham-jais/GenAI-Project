"""
Research Agent service.
Orchestrates multi-step research tasks: paper comparison, literature review,
and research gap detection using the Groq LLM.
"""
import logging
from app.services.llm import chat_completion

logger = logging.getLogger(__name__)


def compare_papers(papers_data: list[dict], focus: str) -> str:
    """
    Compares multiple papers based on their titles, abstracts, and metadata.
    Highlights similarities, differences, and research gaps.
    """
    papers_text = ""
    for i, p in enumerate(papers_data, 1):
        papers_text += (
            f"\n--- Paper {i} ---\n"
            f"Title: {p.get('title', 'N/A')}\n"
            f"Authors: {', '.join(p.get('authors', []))}\n"
            f"Year: {p.get('publication_year', 'N/A')}\n"
            f"Journal: {p.get('journal', 'N/A')}\n"
            f"Abstract: {p.get('abstract', 'No abstract available.')}\n"
        )

    prompt = (
        f"You are an expert academic research analyst.\n"
        f"Compare the following {len(papers_data)} research papers focusing on: {focus}.\n"
        f"Structure your response with these sections:\n"
        f"1. **Overview** - Brief summary of each paper\n"
        f"2. **Common Themes** - Shared methodologies or findings\n"
        f"3. **Key Differences** - Contrasting approaches or conclusions\n"
        f"4. **Research Gaps** - What questions remain unanswered\n"
        f"5. **Recommendation** - Which paper is most impactful and why\n\n"
        f"Papers:\n{papers_text}"
    )
    logger.info(f"Comparing {len(papers_data)} papers...")
    return chat_completion(prompt, temperature=0.4)


def generate_literature_review(topic: str, papers_data: list[dict]) -> str:
    """
    Generates a structured literature review for a research topic
    based on the provided papers.
    """
    papers_text = ""
    for i, p in enumerate(papers_data, 1):
        papers_text += (
            f"\n[{i}] {p.get('title', 'N/A')} "
            f"({p.get('publication_year', 'N/A')}) - "
            f"{', '.join(p.get('authors', []))[:60]}\n"
            f"Abstract: {(p.get('abstract') or 'N/A')[:400]}...\n"
        )

    prompt = (
        f"Write a concise academic literature review on the topic: \"{topic}\".\n"
        f"Base it strictly on the following papers:\n{papers_text}\n\n"
        f"Structure the review as:\n"
        f"1. **Introduction** - Overview of the research area\n"
        f"2. **Current State of Research** - What has been studied\n"
        f"3. **Key Methodologies** - Common approaches used\n"
        f"4. **Major Findings** - Consensus and contradictions\n"
        f"5. **Research Gaps & Future Directions** - Open problems\n"
        f"6. **Conclusion**\n"
        f"Cite papers by their number, e.g., [1], [2]."
    )
    logger.info(f"Generating literature review for topic: {topic}")
    return chat_completion(prompt, temperature=0.3)
