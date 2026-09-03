import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def summarize_paper(abstract: str, title: str) -> str:
    if not abstract:
        return "No abstract available to summarize."
    
    prompt = f"Summarize the following research paper titled '{title}' in simple terms. Highlight the main methodology and findings. Keep it under 3-4 sentences.\n\nAbstract:\n{abstract}"
    
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="openai/gpt-oss-20b",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Error generating summary: {str(e)}"
