from src.state.blog_state import BlogState, Blog, TONE_INSTRUCTIONS
from langchain_core.messages import HumanMessage
from src.state.blog_state import Blog, BlogState

class BlogNode:
    def __init__(self, llm):
        self.llm = llm

    def _get_tone_instruction(self, state:BlogState) -> str:
        tone = state.get("tone", "professional").lower()
        return TONE_INSTRUCTIONS.get(tone, TONE_INSTRUCTIONS["professional"])


    def title_creation(self, state:BlogState) -> dict:
        tone_instructions = self._get_tone_instruction(state)
        
        prompt = (
            "You are an expert blog writer.\n\n"
            "Tone instruction: {tone_instruction}\n\n"
            "Generate a single creative, SEO-friendly blog title for the following topic.\n\n"
            "Topic: {topic}\n\n"
            "Return only the title — no explanation, no quotes, no markdown."
        ).format(topic=state['topic'], tone_instruction = tone_instructions)

        response = self.llm.invoke(prompt)

        return {'blog': Blog(title=response.content.strip(), content="", outline=""),
                "revision_count": 0,
                "quality_score": 0,
                "quality_feedback": ""
                }
        

    def outline_generation(self, state:BlogState) -> dict:
        tone_instructions = self._get_tone_instruction(state)

        if 'topic' in state and state['topic']:
            prompt = (
            "You are an expert blog writer.\n\n"
            "Tone instruction: {tone_instruction}\n\n"
            "Create a detailed, structured outline for a blog post with the following title.\n\n"
            "Title: {title}\n"
            "Topic: {topic}\n\n"
            "The outline should include:\n"
            "- An introduction section\n"
            "- 4-6 main sections with descriptive headings\n"
            "- A conclusion section\n\n"
            "Use markdown formatting (## for headings). Return only the outline."
            ).format(title=state['blog'].title, topic=state['topic'], tone_instruction = tone_instructions)

            response = self.llm.invoke(prompt)
            updated_blog = Blog(
                title=state['blog'].title,
                content = state['blog'].content,
                outline = response.content.strip()
            )
            return {'blog': updated_blog}


    def content_generation(self, state:BlogState) -> dict:
        tone_instructions = self._get_tone_instruction(state)

        feedback_section = ""

        if state.get("quality_feedback"):
            feedback_section = (
                "\n\nIMPORTANT — This is a revision. Your previous attempt scored "
                f"{state.get('quality_score', 0)}/10. Feedback:\n"
                f"{state['quality_feedback']}\n"
                "Address all the feedback points in this revision.\n"
            )

        prompt = (
            "You are an expert blog writer.\n\n"
            "Tone instruction: {tone_instruction}\n\n"
            "Write a detailed, engaging blog post using the title and outline below. "
            "Use markdown formatting.\n\n"
            "Title: {title}\n\n"
            "Outline to follow:\n{outline}\n"
            "{feedback}"
            "\nRequirements:\n"
            "- Minimum 600 words\n"
            "- Use ## and ### headings from the outline\n"
            "- Strictly follow the tone instruction above throughout the entire post\n"
            "- Include a strong introduction and conclusion\n"
            "- No filler phrases like 'In this blog post we will...'"
        ).format(title=state['blog'].title, outline=state['blog'].outline, feedback = feedback_section, tone_instruction = tone_instructions)

        response = self.llm.invoke(prompt)
        updated_blog = Blog(
            title=state['blog'].title,
            outline=state['blog'].outline,
            content = response.content.strip()
        )

        return {'blog': updated_blog}


    def quality_check(self, state:BlogState) -> dict:
        tone = state.get("tone", "professional")

        prompt = (
            "You are a senior editor reviewing a blog post. Evaluate the following "
            "blog and provide a quality score from 0-10 and specific feedback.\n\n"
            "Title: {title}\n\n"
            "Content:\n{content}\n\n"
            "Expected tone: {tone}\n\n"
            "Score criteria:\n"
            "- 8-10: Excellent — detailed, well-structured, engaging, 600+ words, matches expected tone\n"
            "- 5-7: Acceptable — decent but missing depth, structure, length, or tone consistency\n"
            "- 0-4: Poor — too short, off-topic, poorly structured, generic, or wrong tone\n\n"
            "Respond in EXACTLY this format (no extra text):\n"
            "SCORE: <number 0-10>\n"
            "FEEDBACK: <one paragraph of specific, actionable feedback>"
        ).format(title=state['blog'].title, content = state['blog'].content, tone= tone)

        response = self.llm.invoke(prompt)
        lines = response.content.strip().splitlines()

        score = 0
        feedback = "No feedback provided."
        for line in lines:
            if line.startswith("SCORE:"):
                try:
                    score = int(line.replace("SCORE: ", "").strip())
                except ValueError:
                    score = 5
            if line.startswith("FEEDBACK:"):
                feedback = line.replace("FEEDBACK: ", "").strip()

        return {"quality_score": score, "quality_feedback": feedback, "revision_count": state.get('revision_count', 0) + 1,}
    

    def quality_decision(self, state:BlogState) -> str:
        max_revisions = 3
        passing_score = 7

        if state['quality_score'] >= passing_score:
            return "approved"
        if state.get("revision_count", 0) >= max_revisions:
            return "approved"
        return "revise"   


    def translation(self, state:BlogState) -> dict: 
        # """
        #     Translate the generated blog
        # """
        # translation_prompt = """
        #                     Translate the following content into the given language{current_language}.
        #                     Original blog: {blog_content}
        # """
        # blog_content = state['blog']['content']
        # message = [
        #     HumanMessage(translation_prompt.format(current_language=state['current_language'], blog_content=blog_content))
        # ]
        # translated_content = self.llm.with_structured_output(BlogState).invoke(message)

        prompt = (
            "Translate the following blog post into {language}. "
            "Preserve all markdown formatting (headings, bold, etc.).\n\n"
            "Title: {title}\n\n"
            "Content:\n{content}\n\n"
            "Return the translated title on the first line prefixed with 'TITLE: ', "
            "then the translated content after a blank line."
        ).format(language=state['current_language'], title=state['blog'].title, content=state['blog'].content)

        response = self.llm.invoke([HumanMessage(content=prompt)])
        lines = response.content.strip().splitlines()

        translated_title = state['blog'].title
        translated_content = response.content.strip()

        if lines and lines[0].startswith("TITLE:"):
            translated_title = lines[0].replace("TITLE:", "").strip()
            translated_content = "\n".join(lines[2:]).strip()

        updated_blog = Blog(
            title=translated_title,
            outline=state['blog'].outline,
            content=translated_content
        )

        return {"blog": updated_blog}


    def route(self, state: BlogState) -> dict:
        return {"current_language": state['current_language']}
    

    def route_decision(self, state: BlogState) -> str:
        language = state.get("current_language", "").lower()
        supported_languages = {'hindi', 'marathi', 'french'}

        return language if language in supported_languages else "end"