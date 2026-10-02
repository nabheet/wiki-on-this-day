from unittest.mock import MagicMock

import pytest

from tools import video
from tools.video import NewsVideoGeneratorTool


@pytest.fixture
def generator(monkeypatch):
    """Video tool with the OpenAI client mocked out."""
    client = MagicMock()
    monkeypatch.setattr(video, "OpenAI", MagicMock(return_value=client))
    gen = NewsVideoGeneratorTool()
    gen.client = client
    return gen


def test_default_model_is_sora_2(generator):
    assert generator.model == "sora-2"


def test_prompt_exposes_script_variable(generator):
    assert "script" in generator.prompt_template.input_variables


def test_generate_video_returns_video_id(generator):
    generator.client.videos.create_and_poll.return_value = MagicMock(id="video_123")

    assert generator.generate_video("A narrated chunk.") == "video_123"

    kwargs = generator.client.videos.create_and_poll.call_args.kwargs
    assert kwargs["model"] == "sora-2"
    assert kwargs["seconds"] == "12"
    assert "A narrated chunk." in kwargs["prompt"]


def test_generate_video_honours_custom_model(monkeypatch):
    monkeypatch.setattr(video, "OpenAI", MagicMock())
    assert NewsVideoGeneratorTool(model="sora-2-pro").model == "sora-2-pro"


def test_download_video_streams_to_file(generator, tmp_path):
    target = tmp_path / "clip_0.mp4"

    generator.download_video("video_123", target)

    download = generator.client.videos.with_streaming_response.download_content
    download.assert_called_once_with(video_id="video_123")
    streamed = download.return_value.__enter__.return_value
    streamed.stream_to_file.assert_called_once_with(target)


def test_delete_video_deletes_by_id(generator):
    generator.delete_video("video_123")
    generator.client.videos.delete.assert_called_once_with(video_id="video_123")


def test_list_videos_returns_data(generator):
    videos = [MagicMock(), MagicMock()]
    generator.client.videos.list.return_value = MagicMock(data=videos)

    assert generator.list_videos() == videos
