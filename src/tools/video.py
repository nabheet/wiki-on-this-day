from pathlib import Path
from openai import OpenAI
from openai.types.video import Video
from langchain_core.prompts import PromptTemplate


class NewsVideoGeneratorTool:
    """
    Generates a narrated news anchor video using OpenAI Sora.
    """

    def __init__(self, model: str = "sora-2"):
        self.client = OpenAI()
        self.model = model
        dir = Path(__file__).parent.parent
        prompt_text = Path(f"{dir}/prompts/documentary_anchor_video.txt").read_text()
        self.prompt_template = PromptTemplate.from_template(prompt_text)

    def generate_video(self, script: str) -> str:
        response = self.client.videos.create_and_poll(
            model=self.model,
            prompt=self.prompt_template.format(script=script),
            seconds="12",
        )
        print("Video generated:", response.id)
        return response.id

    def download_video(self, video_id: str, output_path: Path) -> None:
        with self.client.videos.with_streaming_response.download_content(
            video_id=video_id
        ) as response:
            response.stream_to_file(output_path)
        print(f"Video downloaded to: {output_path}")

    def delete_video(self, video_id: str) -> None:
        self.client.videos.delete(video_id=video_id)
        print(f"Deleted video with ID: {video_id}")

    def list_videos(self) -> list[Video]:
        videos = self.client.videos.list()
        return videos.data
