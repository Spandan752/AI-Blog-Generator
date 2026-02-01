# AI Blog Generator

Generate high-quality blog posts in seconds using AI-powered templates and customizable prompts. AI Blog Generator helps writers, content teams, and creators produce SEO-friendly, well-structured articles quickly while keeping full control over tone, length, and formatting.

## Features

- Generate full-length blog posts from a title or prompt
- Multiple templates (listicle, how-to, longform, SEO-optimized, etc.)
- Customizable tone, length, and target audience
- Support for images, metadata (title, description, tags), and SEO fields
- Multi-language support (add prompts for different locales)
- Simple UI for iterating on generated content and re-generating sections
- Audit logs and generation history (if using a DB)

## Tech stack

- Python
- LangGraph
- LangSmith
- Groq AI API
- FastAPI
- Uvicorn
- Streamlit
- AWS

## Quickstart

1. Clone the repo
   ```bash
   git clone https://github.com/Spandan752/AI-Blog-Generator.git
   cd AI-Blog-Generator
   ```

2. Create and activate a virtual environment (recommended)
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # macOS / Linux
   .venv\Scripts\activate      # Windows
   pip install --upgrade pip
   ```

3. Install dependencies
   Note: The repository does not include a requirements.txt. Install packages used in the code:
   ```bash
   pip install fastapi uvicorn python-dotenv langchain-groq langgraph langchain-core
   ```
   If you prefer, create a requirements.txt after confirming exact package versions in your environment.

4. Environment variables
   Create a `.env` in the project root with at least the following keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   LANGCHAIN_API_KEY=your_langchain_or_langsmith_api_key_here
   ```
   The app sets `LANGSMITH_API_KEY` from `LANGCHAIN_API_KEY` at runtime. Adjust as necessary for your deployment.

5. Run the app (development)
   ```bash
   uvicorn app:app --reload --port 8000
   ```
   The app listens on port 8000 by default (app.py sets the same when run directly).

## Usage overview

- Provide a title or short prompt and choose a template.
- Adjust tone, length, and SEO fields.
- Click "Generate" to create article drafts.
- Edit the generated content in-app, save drafts, and export as Markdown/HTML.
- Optionally connect publishing integrations (WordPress, Ghost, custom CMS) or schedule posts.

## Configuration

- LLM provider: Configure the API key and optionally model or temperature settings.
- Templates: Add or edit templates to match your editorial style.
- Persistence: Configure a database connection for saving drafts and history.
- Auth: Enable authentication for team workflows and per-user history.

## Examples of env variables

- OPENAI_API_KEY — API key for the AI provider
- DATABASE_URL — Optional DB connection string
- NEXTAUTH_URL — If using NextAuth or similar auth
- SITE_URL — Public deployment URL used for metadata and OAuth redirects

## Roadmap / Ideas

- Add more templates and writing tones
- Fine-grained prompt presets per industry (tech, finance, health, lifestyle)
- Team collaboration (shared drafts, comments)
- Built-in image generation and media library
- Publish integrations (WordPress, Medium, Ghost)
- Rate limiting and cost controls for API usage
