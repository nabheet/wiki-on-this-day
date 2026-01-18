
# On This Day Agentic Documentary Video Generator

This project uses **LangChain (modern, non-classic)** to build an agentic system that:

1. Downloads "On this day" historical events from Wikipedia
2. Ensures every event is date-associated
3. Uses an OpenAI LLM (via LangChain) to rewrite events as a documentary script
4. Uses OpenAI Sora to generate a **documentary presenter video with audio**
5. Produces a downloadable video

## Architecture

- agents/ – High-level agent orchestration
- chains/ – LLM chains for summarization and script generation
- tools/ – External tools (Wikipedia fetcher, video generator)
- prompts/ – Prompt templates
- memory/ – Conversation/state memory
- tests/ – Unit tests for every class

## AI Generation Prompt

ChatGPT 5.2 was used to generate the initial version of this code using the prompt in `generation_prompt.txt`. There was significant amount of time spent debugging and refactoring
the generated code. However, it works now. One of the refactors involved splitting the
generated text into smaller chunks so Sora could generate the video via API within its
limits. After downloading the individual files, I asked ChatGPT to generate code for
stitching the video files into one file.

## Install

```bash
uv pip install -r pyproject.toml
```

## Run

```bash
uv run python -m main
```

## Environment Variables

- `OPENAI_API_KEY`

## Notes

- Wikipedia access uses **requests only**
- No `langchain_classic`
- Follows SOLID / DRY / KISS / YAGNI principles
