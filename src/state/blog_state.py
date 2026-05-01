from typing import TypedDict
from pydantic import BaseModel, Field

class Blog(BaseModel):
    title:str=Field(description='The title of the blog.')
    outline:str=Field(description='The outline of the blog.', default="")
    content:str=Field(description='Main content of the blog', default="")



class BlogState(TypedDict):
    topic:str
    blog:Blog
    current_language:str
    quality_score:int
    quality_feedback:str
    revision_count: int