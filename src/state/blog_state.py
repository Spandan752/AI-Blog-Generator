from typing import TypedDict
from pydantic import BaseModel, Field

class Blog(BaseModel):
    title:str=Field(description='The title of the blog.')
    content:str=Field(description='Main content of the blog')

class BlogState(TypedDict):
    topic:str
    blog:Blog
    current_language:str