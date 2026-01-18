from agents.documentary_agent import OnThisDayDocumentaryAgent


def main():
    agent = OnThisDayDocumentaryAgent()
    video_path = agent.run()
    print("Video generated:", video_path)


if __name__ == "__main__":
    main()
