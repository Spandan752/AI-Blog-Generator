from langgraph.graph import START, END, StateGraph
from src.LLMs.groqllm import GroqLLM
from src.state.blog_state import BlogState
from src.nodes.blog_node import BlogNode


class GraphBuilder:
    def __init__(self, llm):
        self.llm = llm
        # self.graph = StateGraph(BlogState)   #remove this


    def _add_common_nodes(self, graph: StateGraph, blog_node: BlogNode):
        """Add common nodes to the graph"""

        graph.add_node("title_creation", blog_node.title_creation)
        graph.add_node("outline_generation", blog_node.outline_generation)
        graph.add_node("content_generation", blog_node.content_generation)
        graph.add_node("quality_check", blog_node.quality_check)


    def _add_quality_loop(self, graph: StateGraph, blog_node: BlogNode, next_node: str):
        """Add a loop for quality check and improvement"""

        graph.add_conditional_edge(
            "quality_check",
            blog_node.quality_decision, {
            "revise": "content_generation",       # loop back
            "approved": next_node,                # move forward
            },
        )


    def build_topic_graph(self) -> StateGraph:
        """Build a graph to generate blog for given topic"""

        graph = StateGraph(BlogState)
        blog_node = BlogNode(self.llm)

        self._add_common_nodes(graph, blog_node)

        # self.blog_node_obj = BlogNode(self.llm)
        # # Define nodes
        # self.graph.add_node("title_creation", self.blog_node_obj.title_creation)
        # self.graph.add_node("content_generation", self.blog_node_obj.content_generation)

        # Add edges
        graph.add_edge(START, 'title_creation')
        graph.add_edge('title_creation', 'outline_generation')
        graph.add_edge('outline_generation', 'content_generation')
        graph.add_edge('content_generation', 'quality_check')
        self._add_quality_loop(graph, blog_node, next_node=END)
        # graph.add_edge('quality_check', END)

        return graph
    

    def build_language_graph(self) -> StateGraph:
        """Build a graph to generate blog in different languages"""
        graph = StateGraph(BlogState)
        blog_node = BlogNode(self.llm)

        self._add_common_nodes(graph, blog_node)

        # translation nodes
        graph.add_node("hindi_translation", blog_node.translation)
        graph.add_node("marathi_translation", blog_node.translation)    
        graph.add_node("french_translation", blog_node.translation)
        graph.add_node("route", blog_node.route)

        # Edges
        graph.add_edge(START, 'title_creation')
        graph.add_edge('title_creation', 'outline_generation')
        graph.add_edge('outline_generation', 'content_generation')
        graph.add_edge('content_generation', 'quality_check')

        # quality loop
        self._add_quality_loop(graph, blog_node, next_node="route")

        # Language routing
        graph.add_conditional_edges(
            "route",
            blog_node.route_decision, {
                "hindi": "hindi_translation",
                "marathi": "marathi_translation",
                "french": "french_translation",
                "end": END
            },
        )

        graph.add_edge("hindi_translation", END)
        graph.add_edge("marathi_translation", END)
        graph.add_edge("french_translation", END)

        return graph


    def setup_graph(self, usecase):
        """Compile the graph based on usecase"""
        if usecase == 'topic':
            return self.build_topic_graph().compile()
        if usecase == 'language':
            return self.build_language_graph().compile()
        raise ValueError(f"Unknown usecase: '{usecase}'. Must be 'topic' or 'language'.")
    

# Below code is written for langsmith deployments

def get_graph():
    llm = GroqLLM().get_llm()
    return GraphBuilder(llm).build_topic_graph().compile()


graph = get_graph()