from datetime import date
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from agents import documentary_agent
from agents.documentary_agent import OnThisDayDocumentaryAgent


def _script(chunk_count: int) -> str:
    return "\n\n".join(f"chunk {i}" for i in range(chunk_count))


@pytest.fixture
def agent(monkeypatch):
    """Agent with every external collaborator replaced by a mock."""
    for collaborator in (
        "WikipediaOnThisDayTool",
        "NewsScriptChain",
        "NewsVideoGeneratorTool",
        "VideoStitcherTool",
    ):
        monkeypatch.setattr(documentary_agent, collaborator, MagicMock())
    return OnThisDayDocumentaryAgent()


def test_run_formats_events_and_delegates_video_generation(agent, monkeypatch):
    agent.wiki.fetch.return_value = [
        {"date": "1969-7-20", "sort_key": 1969, "text": "Apollo 11 lands"},
        {"date": "1945-7-20", "sort_key": 1945, "text": "World War II ends"},
    ]
    agent.chain.run.return_value = _script(3)
    final = Path("/tmp/final.mp4")
    monkeypatch.setattr(agent, "generate_long_video", MagicMock(return_value=final))

    assert agent.run() == str(final)

    agent.wiki.fetch.assert_called_once_with(date.today())
    formatted = agent.chain.run.call_args.args[0]
    assert "1969-7-20 — Apollo 11 lands" in formatted
    assert "1945-7-20 — World War II ends" in formatted
    agent.generate_long_video.assert_called_once_with(_script(3))


@pytest.mark.parametrize("script", ["", "single chunk", "chunk 0\n\nchunk 1"])
def test_generate_long_video_requires_at_least_three_chunks(agent, script):
    assert agent.generate_long_video(script) is None
    agent.video.generate_video.assert_not_called()
    agent.stitcher.stitch.assert_not_called()


def test_generate_long_video_generates_downloads_deletes_and_stitches(agent, monkeypatch):
    monkeypatch.setattr("builtins.input", MagicMock(return_value="y"))
    agent.video.generate_video.return_value = "video-id"

    result = agent.generate_long_video(_script(3))

    final = Path(f"{agent.outdir}/final_news_video.mp4")
    assert result == final

    assert agent.video.generate_video.call_count == 3
    clips = [Path(f"{agent.outdir}/clip_{i}.mp4") for i in range(3)]
    assert [c.args[1] for c in agent.video.download_video.call_args_list] == clips
    assert agent.video.delete_video.call_count == 3
    agent.stitcher.stitch.assert_called_once_with(clips, final)


def test_generate_long_video_stops_when_user_declines(agent, monkeypatch):
    monkeypatch.setattr("builtins.input", MagicMock(return_value="n"))

    assert agent.generate_long_video(_script(3)) is None

    agent.video.generate_video.assert_not_called()
    agent.stitcher.stitch.assert_not_called()


def test_generate_long_video_honours_chunk_limit(agent, monkeypatch):
    monkeypatch.setattr("builtins.input", MagicMock(return_value="y"))

    agent.generate_long_video(_script(5))

    # Only the first CHUNK_LIMIT chunks are rendered, even with more available.
    assert agent.CHUNK_LIMIT == 3
    assert agent.video.generate_video.call_count == agent.CHUNK_LIMIT
