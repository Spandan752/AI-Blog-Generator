import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import json
import os
from dotenv import load_dotenv

from src.graphs.graph_builder import GraphBuilder
from src.LLMs.groqllm import GroqLLM

load_dotenv()

app = FastAPI()

os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')
os.environ['LANGCHAIN_TRACING_V2'] = 'true'
os.environ['LANGCHAIN_PROJECT'] = 'AI-blog-generator'


# Schemas

class BlogRequest(BaseModel):
    topic: str = Field(..., min_length=3, description='The topic for the blog post')
    language: str = Field(default="", description='Target language for the blog post')
    tone:str = Field(default="professional", description='Tone of the blog post. Supported values: professional, casual, academic, humorous')


class BlogResponse(BaseModel):
    title: str
    outline: str
    content: str
    language: str
    tone: str
    quality_score: int
    revision_count: int


# App lifecycle
# Initiating the app and graphbuilder once to optimize performance

@asynccontextmanager
async def lifespan(app: FastAPI):
    global graph_builder
    llm = GroqLLM().get_llm()
    graph_builder = GraphBuilder(llm)
    yield 

app = FastAPI(
    title="AI Blog Generator",
    description="An API to generate blog posts using AI based on a given topic and language.",
    version="1.0.0",
    lifespan=lifespan
)


# Endpoints

@app.get("/", tags=["Health Check"])
def health_check():
    return {"status": "ok", "message": "AI Blog Generator API is running."}


@app.post("/blogs", response_model = BlogResponse, tags=["Blog"])
async def create_blogs(request: BlogRequest):
    """Generate a blog post for the given topic.
 
    Runs the full agentic pipeline:
    title -> outline -> content -> quality_check (loop if needed) ->[translation]
    """

    SUPPORTED_TONES = {"professional", "casual", "academic", "humorous"}
    if request.tone.lower() not in SUPPORTED_TONES:
        raise HTTPException(status_code=400, detail=f"Unsupported tone '{request.tone}'. Supported tones are: {', '.join(SUPPORTED_TONES)}")

    try:
        usecase = 'language' if request.language.strip() else 'topic'
        graph = graph_builder.setup_graph(usecase=usecase)

        initial_state = {
            "topic": request.topic,
            "current_language": request.language.strip().lower(),
            "tone": request.tone.lower(),
            "revision_count": 0,
            "quality_score": 0,
            "quality_feedback": ""
        }

        state = graph.invoke(initial_state)
        blog = state['blog']
        
        return BlogResponse(
            title=blog.title,
            outline=blog.outline,
            content=blog.content,
            language=state.get("current_language", "english"),
            quality_score=state.get("quality_score", 0),
            revision_count=state.get("revision_count", 0),
            tone=state.get("tone", "professional"),
        )
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.post("/blogs/stream", tags=["Blog"])
async def create_blog_stream(request: BlogRequest):
    """Stream blog generation events as they happen through the graph.
    """

    SUPPORTED_TONES = {"professional", "casual", "academic", "humorous"}
    if request.tone.lower() not in SUPPORTED_TONES:
        raise HTTPException(status_code=400, detail=f"Unsupported tone '{request.tone}'. Supported tones are: {', '.join(SUPPORTED_TONES)}")



    try:
        usecase = "language" if request.language.strip() else "topic"
        graph = graph_builder.setup_graph(usecase=usecase)

        initial_state = {
            "topic": request.topic,
            "current_language": request.language.lower().strip(),
            "revision_count": 0,
            "quality_score": 0,
            "quality_feedback": "",
            "tone": request.tone.lower()
        }

        def event_stream():
            for event in graph.stream(initial_state, stream_mode="updates"):
                for node_name, node_output in event.items():
                    payload = {
                        "node": node_name,
                        "quality_score": node_output.get("quality_score"),
                        "revision_count": node_output.get("revision_count")
                    }

                    if "blog" in node_output and node_output["blog"]:
                        payload["title"] = node_output["blog"].title
                    yield json.dumps(payload) + "\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Streamling failed:{str(e)}")



if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', reload=True, port=8000)
