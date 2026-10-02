import logging
from pathlib import Path
from unittest.mock import MagicMock

import main


def test_main_runs_the_agent_and_logs_the_output_path(monkeypatch, caplog):
    agent = MagicMock()
    agent.run.return_value = Path("/tmp/final_news_video.mp4")
    monkeypatch.setattr(main, "OnThisDayDocumentaryAgent", MagicMock(return_value=agent))

    with caplog.at_level(logging.INFO):
        main.main()

    agent.run.assert_called_once_with()
    assert "Video generated: /tmp/final_news_video.mp4" in caplog.text


def test_main_logs_none_when_no_video_was_produced(monkeypatch, caplog):
    agent = MagicMock()
    agent.run.return_value = None
    monkeypatch.setattr(main, "OnThisDayDocumentaryAgent", MagicMock(return_value=agent))

    with caplog.at_level(logging.INFO):
        main.main()

    assert "Video generated: None" in caplog.text
