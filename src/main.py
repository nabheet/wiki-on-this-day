from agents.documentary_agent import OnThisDayDocumentaryAgent
from logging import getLogger, basicConfig

basicConfig(level="INFO")

logger = getLogger(__name__)


def main():
    agent = OnThisDayDocumentaryAgent()
    video_path = agent.run()
    logger.info(f"Video generated: {video_path}")


if __name__ == "__main__":
    main()
