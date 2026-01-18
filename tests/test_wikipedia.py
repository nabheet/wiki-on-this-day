from datetime import date
from tools.wikipedia import WikipediaOnThisDayTool


def test_fetch():
    tool = WikipediaOnThisDayTool()
    events = tool.fetch(date(2020, 1, 1))
    assert isinstance(events, list)
