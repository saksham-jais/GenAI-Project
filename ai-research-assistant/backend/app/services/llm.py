"""
LLM service — Groq client wrapper.
Single source of truth for LLM configuration and model selection.
"""
import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

DEFAULT_MODEL = "openai/gpt-oss-20b"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def chat_completion(prompt: str, model: str = DEFAULT_MODEL, temperature: float = 0.3) -> str:
    """
    Send a prompt to the Groq LLM and return the text response.
    """
    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=model,
            temperature=temperature,
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"LLM call failed: {e}")
        raise


def summarize_abstract(title: str, abstract: str) -> str:
    """Generate a plain-language summary of a paper abstract."""
    prompt = (
        f"Summarize the research paper titled '{title}' in 3-4 simple sentences. "
        f"Highlight the main methodology and key findings.\n\nAbstract:\n{abstract}"
    )
    return chat_completion(prompt)
