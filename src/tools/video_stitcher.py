from pathlib import Path
from moviepy import VideoFileClip, concatenate_videoclips


class VideoStitcherTool:
    def stitch(self, clips: list[Path], output_path: Path) -> None:
        video_clips = [VideoFileClip(str(p)) for p in clips]

        final = concatenate_videoclips(video_clips, method="compose")
        final.write_videofile(
            str(output_path),
            codec="libx264",
            audio_codec="aac",
            fps=24,
        )

        for clip in video_clips:
            clip.close()
