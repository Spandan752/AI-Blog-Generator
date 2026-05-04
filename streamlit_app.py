import streamlit as st
import requests
import json

API_URL = "https://ai-blog-generator-api-favc.onrender.com"

# Setting page configuration

st.set_page_config(
    page_title="AI Blog Generator",
    page_icon="✍️",
    layout="wide"
)

# Styles

st.markdown("""
<style>
    .block-container { padding-top: 2rem; }
    .blog-title { font-size: 2rem; font-weight: 700; margin-bottom: 0.5rem; }
    .meta-badge {
        display: inline-block;
        background: #f0f2f6;
        border-radius: 12px;
        padding: 4px 12px;
        font-size: 0.8rem;
        margin-right: 8px;
        color: #444;
    }
    .score-high { color: #22c55e; font-weight: 700; }
    .score-mid  { color: #f59e0b; font-weight: 700; }
    .score-low  { color: #ef4444; font-weight: 700; }
    .node-step {
        padding: 6px 0;
        font-size: 0.9rem;
        color: #555;
    }
</style>
""", unsafe_allow_html=True)

# Header and sidebar

st.title("AI Blog Generator ✍️")
st.caption("Generate a blog post using AI")

with st.sidebar:
    st.header("Blog settings")

    topic = st.text_input(
        label="Blog topic", 
        placeholder="eg. 'The future of AI in healthcare'",
        max_chars=100,
        help="Enter the topic for your blog post."
    )

    tone = st.selectbox(
        label="Tone of the blog",
        options=["professional", "casual", "academic", "humorous"],
        help="Select the tone for your blog post.",
        index=0
    )

    language = st.selectbox(
        label="Select language for the blog",
        options=["English", "Hindi", "Marathi", "French"],
        index=0,
        help="Choose the language for your blog post."
    )

    generate_btn = st.button("Generate", width="stretch", type="primary", shortcut="Enter")

    st.divider()
    st.markdown("Made with ❤️")

# Main area

NODE_LABELS = {
    "title_creation":      "🏷️  Generating title...",
    "outline_generation":  "📋  Building outline...",
    "content_generation":  "✍️  Writing content...",
    "quality_check":       "🔍  Checking quality...",
    "hindi_translation":   "🌐  Translating to Hindi...",
    "marathi_translation": "🌐  Translating to Marathi...",
    "french_translation":  "🌐  Translating to French...",
    "route":               "🔀  Routing to translation...",
}
 
NODE_DONE_LABELS = {
    "title_creation":      "✅  Title created",
    "outline_generation":  "✅  Outline ready",
    "content_generation":  "✅  Content written",
    "quality_check":       "✅  Quality checked",
    "hindi_translation":   "✅  Translated to Hindi",
    "marathi_translation": "✅  Translated to Marathi",
    "french_translation":  "✅  Translated to French",
    "route":               "✅  Language routed",
}

if generate_btn:
    if not topic.strip():
        st.warning("Please enter a valid blog topic.")
        st.stop()
    
    lang_param = "" if language == "English" else language.lower()

    payload = {
        "language": lang_param,
        "tone": tone,
        "topic": topic.strip()
    }

    st.subheader("Generating your blog post...")
    progress_container = st.container()
    step_placeholders = {}
 
    result = None
    error = None

    # with st.container():
    try:
        with requests.post(f"{API_URL}/blogs/stream", json=payload, stream=True, timeout=120) as response:
            response.raise_for_status()

            completed_nodes = []

            for line in response.iter_lines():
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue

                node = event.get("node", "")
                if node in NODE_DONE_LABELS:
                    completed_nodes.append(node)

                with progress_container:
                    for n in completed_nodes:
                        revision = event.get("revision_count")
                        label = NODE_DONE_LABELS.get(n, f"✅ {n}")
                        if n == "quality_check" and revision:
                            label += f"  (revision {revision})"
                        st.markdown(f'<div class="node-step">{label}</div>', unsafe_allow_html=True)

        blog_content = requests.post(f"{API_URL}/blogs", json=payload, timeout=120)
        blog_content.raise_for_status()
        blog_data = blog_content.json()

    except requests.exceptions.ConnectionError:
        error = "Cannot connect to the API. Make sure the FastAPI server is running on port 8000."
    except requests.exceptions.Timeout:
        error = "Request timed out. The blog is taking longer than expected — try a simpler topic."
    except requests.exceptions.HTTPError as http_err:
        error = f"HTTP error occured: {http_err}"

    if error:
        st.error(error)
        st.stop()

# Show results

    st.divider()
    # st.markdown(f'<div class="blog-title">{blog_data["title"]}</div>', unsafe_allow_html=True)

    st.markdown(f"\n\n{blog_data['content']}")
    st.download_button(
        label = "Download",
        data = f"# {blog_data['title']}\n\n{blog_data['content']}",
        file_name = f"{blog_data['title'].replace(' ', '_')}.pdf",
        mime = "text/markdown",
        icon=":material/download:"
    )

else:
    st.info("Enter a blog topic and click 'Generate' to create your AI-generated blog post.")

            
