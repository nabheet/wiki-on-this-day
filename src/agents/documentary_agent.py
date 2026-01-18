from datetime import date
from pathlib import Path
from tools.video_stitcher import VideoStitcherTool
from tools.wikipedia import WikipediaOnThisDayTool
from chains.documentary_chain import NewsScriptChain
from tools.video import NewsVideoGeneratorTool
from logging import getLogger

logger = getLogger(__name__)


class OnThisDayDocumentaryAgent:
    def __init__(self):
        self.wiki = WikipediaOnThisDayTool()
        self.chain = NewsScriptChain()
        self.video = NewsVideoGeneratorTool()
        self.stitcher = VideoStitcherTool()
        self.outdir = f"{Path(__file__).parent.parent.parent}/output"
        self.CHUNK_LIMIT = 3

    def run(self) -> str:
        today = date.today()
        events = self.wiki.fetch(today)

        formatted = "\n".join(f"{e['date']} — {e['text']}" for e in events)

        script = self.chain.run(formatted)

        logger.info("\n****Generated script****")
        logger.info(script)
        logger.info("************************\n")
        return str(self.generate_long_video(script))

    def generate_long_video(self, script: str) -> Path | None:
        chunks = script.split("\n\n")
        clip_paths: list[Path] = []

        if len(chunks) == 0:
            logger.error("\n\nNo script chunks to process.\n\n")
            return None

        if len(chunks) < self.CHUNK_LIMIT:
            logger.error("\n\nNot enough chunks to generate a long video.\n\n")
            return None

        logger.info(f"\nGenerating long video ({len(chunks)} chunks)...")
        for i, chunk in enumerate(chunks):
            if i >= self.CHUNK_LIMIT:
                break
            logger.info(f"\n\n****Generating video for chunk {i + 1}****")
            logger.info(chunk)
            ans = input("Continue? (y/N): ")
            if ans.lower() != "y":
                return None
            video_id = self.video.generate_video(chunk)
            clip_path = Path(f"{self.outdir}/clip_{i}.mp4")
            self.video.download_video(video_id, clip_path)
            clip_paths.append(clip_path)
            self.video.delete_video(video_id)
            logger.info("*******************************")
        final_path = Path(f"{self.outdir}/final_news_video.mp4")
        self.stitcher.stitch(clip_paths, final_path)
        return final_path
