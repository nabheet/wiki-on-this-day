from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from pathlib import Path
from utils.settings import settings


class NewsScriptChain:
    def __init__(self):
        dir = Path(__file__).parent.parent
        prompt_text = Path(f"{dir}/prompts/documentary_anchor_script.txt").read_text()
        self.prompt = PromptTemplate.from_template(prompt_text)
        self.llm = ChatOpenAI(api_key=settings.openai_api_key, temperature=0.7)

    def run(self, events: str) -> str:
        return str(self.llm.invoke(self.prompt.format(events=events)).content)
