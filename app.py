import uvicorn
from fastapi import FastAPI, Request
from src.graphs.graph_builder import GraphBuilder
from src.LLMs.groqllm import GroqLLM
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

os.environ['LANGSMITH_API_KEY'] = os.getenv('LANGCHAIN_API_KEY')

@app.post("/blogs")
async def create_blogs(request: Request):
    data = await request.json()
    topic = data.get("topic", "")
    language = data.get("language", "")

    # get the LLM
    groqllm = GroqLLM()
    llm = groqllm.get_llm()

    # get the graph
    graphbuilder = GraphBuilder(llm)
    if topic and language:
        print(topic, language)
        graph = graphbuilder.setup_graph(usecase='language')
        state =graph.invoke({'topic': topic, 'current_language': language.lower()})
    elif topic:
        graph = graphbuilder.setup_graph(usecase='topic')
        state =graph.invoke({'topic': topic})
    return {'data': state}

if __name__ == '__main__':
    uvicorn.run('app:app', host='0.0.0.0', reload=True, port=8000)
