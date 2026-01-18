import requests
from datetime import date


class WikipediaOnThisDayTool:
    """Fetches 'On this day' content from Wikipedia."""

    WIKI_API = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/events"

    def fetch(self, target_date: date) -> list[dict]:
        try:
            url = f"{self.WIKI_API}/{target_date.month}/{target_date.day}"
            headers = {"User-Agent": "WikiOnThisDayBot/1.0"}
            resp = requests.get(url=url, headers=headers, timeout=10)
            resp.raise_for_status()
            data = resp.json()

            events = []
            for e in data.get("events", []):
                events.append(
                    {
                        "date": f"{e['year']}-{target_date.month}-{target_date.day}",
                        "sort_key": e["year"],
                        "text": e["text"],
                    }
                )
                events.sort(key=lambda x: x["sort_key"])
            return events
        except Exception as e:
            raise RuntimeError(f"Wikipedia fetch failed: {e}")
