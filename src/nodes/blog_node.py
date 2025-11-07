from src.state.blog_state import BlogState
from langchain_core.messages import SystemMessage, HumanMessage
from src.state.blog_state import Blog, BlogState

class BlogNode:
    def __init__(self, llm):
        self.llm = llm

    def title_creation(self, state:BlogState):
        if "topic" in state and state['topic']:
            prompt = """
                    You are an expert Blog writer. Use markdown formatting and generate a blog title for {topic}. This title should br creative and SEO friendly.
                    """
            system_message = prompt.format(topic=state['topic'])
            response = self.llm.invoke(system_message)
            return {'blog': {'title': response.content}}
        
    def content_generation(self, state:BlogState):
        if 'topic' in state and state['topic']:
            prompt = """
                    You are an expert Blog writer. Use markdown formatting and generate a detailed blog content for {topic}.
                     """
            system_message = prompt.format(topic=state['topic'])
            response = self.llm.invoke(system_message)
            return {'blog': {'title': state['blog']['title'], 'content': response.content}}
        
    def translation(self, state:BlogState):
        """
            Translate the generated blog
        """
        translation_prompt = """
                            Translate the following content into the given language{current_language}.
                            Original blog: {blog_content}
        """
        blog_content = state['blog']['content']
        message = [
            HumanMessage(translation_prompt.format(current_language=state['current_language'], blog_content=blog_content))
        ]
        translated_content = self.llm.with_structured_output(BlogState).invoke(message)

    def route(self, state: BlogState):
        return {"current_language": state['current_language']}
    

    def route_decision(self, state: BlogState):
        if state['current_language'] == 'hindi':
            return "hindi"
        if state['current_language'] == 'marathi':
            return "marathi"
        if state['current_language'] == 'french':
            return "french"
        else:
            return state['current_language']
