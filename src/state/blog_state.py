from typing import TypedDict, Literal
from pydantic import BaseModel, Field

class Blog(BaseModel):
    title:str=Field(description='The title of the blog.')
    outline:str=Field(description='The outline of the blog.', default="")
    content:str=Field(description='Main content of the blog', default="")

SUPPORTED_TONE = Literal["professional", "casual", "academic", "humorous"]

TONE_INSTRUCTIONS = {
    "professional": (
        "Write in a professional, authoritative tone. Use clear, precise language. "
        "Avoid slang or overly casual phrasing. Structure arguments logically."
    ),
    "casual": (
        "Write in a friendly, conversational tone — like you're explaining to a friend. "
        "Use contractions, simple language, and a warm approachable style. "
        "Short sentences are fine. Avoid jargon."
    ),
    "academic": (
        "Write in a formal academic tone. Use discipline-specific terminology where appropriate. "
        "Support claims with reasoning. Avoid colloquialisms. "
        "Structure content with clear thesis points and evidence-based arguments."
    ),
    "humorous": (
        "Write in a witty, humorous tone. Use clever wordplay, light sarcasm, and entertaining "
        "analogies. Keep it fun and engaging while still being informative. "
        "Don't force jokes — let the humor arise naturally from the content."
    ),
}

class BlogState(TypedDict):
    topic:str
    blog:Blog
    current_language:str
    quality_score:int
    quality_feedback:str
    revision_count: int
    tone : str