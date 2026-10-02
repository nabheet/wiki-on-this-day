from unittest.mock import MagicMock

import pytest

from chains import documentary_chain
from chains.documentary_chain import NewsScriptChain


@pytest.fixture
def llm(monkeypatch):
    """Patch ChatOpenAI so no network call or API key is ever needed."""
    fake_llm = MagicMock()
    monkeypatch.setattr(documentary_chain, "ChatOpenAI", MagicMock(return_value=fake_llm))
    return fake_llm


def test_prompt_exposes_events_variable(llm):
    chain = NewsScriptChain()
    assert "events" in chain.prompt.input_variables


def test_llm_is_configured_with_temperature(llm, monkeypatch):
    monkeypatch.setattr(documentary_chain, "ChatOpenAI", MagicMock())
    NewsScriptChain()

    _, kwargs = documentary_chain.ChatOpenAI.call_args
    assert kwargs["temperature"] == 0.7
    assert kwargs["api_key"] is not None


def test_run_sends_formatted_prompt_and_returns_text(llm):
    llm.invoke.return_value = MagicMock(content="A narrated history of the day.")

    script = NewsScriptChain().run("1945-7-20 — World War II ends")

    assert script == "A narrated history of the day."
    prompt_sent = llm.invoke.call_args.args[0]
    assert "1945-7-20 — World War II ends" in prompt_sent


def test_run_coerces_non_string_llm_content(llm):
    llm.invoke.return_value = MagicMock(content=42)
    assert NewsScriptChain().run("events") == "42"
