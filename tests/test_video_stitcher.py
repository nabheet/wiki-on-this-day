from pathlib import Path
from unittest.mock import MagicMock, call

import pytest

from tools import video_stitcher
from tools.video_stitcher import VideoStitcherTool


@pytest.fixture
def moviepy_mocks(monkeypatch):
    """Patch the two moviepy entry points so no ffmpeg or media file is needed."""
    clips = [MagicMock(), MagicMock(), MagicMock()]
    file_clip = MagicMock(side_effect=clips)
    concat = MagicMock()
    monkeypatch.setattr(video_stitcher, "VideoFileClip", file_clip)
    monkeypatch.setattr(video_stitcher, "concatenate_videoclips", concat)
    return file_clip, concat, clips


def test_stitch_concatenates_clips_and_writes_output(moviepy_mocks):
    file_clip, concat, clips = moviepy_mocks
    sources = [Path("clip_0.mp4"), Path("clip_1.mp4"), Path("clip_2.mp4")]
    target = Path("final_news_video.mp4")

    VideoStitcherTool().stitch(sources, target)

    assert file_clip.call_args_list == [call(str(p)) for p in sources]
    assert concat.call_args.args == (clips,)
    assert concat.call_args.kwargs == {"method": "compose"}

    write = concat.return_value.write_videofile.call_args
    assert write.args == (str(target),)
    assert write.kwargs == {"codec": "libx264", "audio_codec": "aac", "fps": 24}


def test_stitch_closes_every_clip(moviepy_mocks):
    _, _, clips = moviepy_mocks
    VideoStitcherTool().stitch([Path("a.mp4"), Path("b.mp4"), Path("c.mp4")], Path("out.mp4"))
    for clip in clips:
        clip.close.assert_called_once()


def test_stitch_opens_no_clips_when_given_an_empty_list(moviepy_mocks):
    file_clip, concat, _ = moviepy_mocks

    VideoStitcherTool().stitch([], Path("out.mp4"))

    file_clip.assert_not_called()
    concat.assert_called_once_with([], method="compose")
