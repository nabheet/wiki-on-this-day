import json
from datetime import date

import pytest
import requests

from tools.wikipedia import WikipediaOnThisDayTool


def _response(payload):
    resp = requests.Response()
    resp.status_code = 200
    resp._content = json.dumps(payload).encode()
    return resp


def _mock_get(monkeypatch, payload=None, side_effect=None):
    calls = []

    def fake_get(**kwargs):
        calls.append(kwargs)
        if side_effect is not None:
            raise side_effect
        return _response(payload)

    monkeypatch.setattr("tools.wikipedia.requests.get", fake_get)
    return calls


def test_fetch_parses_events_oldest_first(monkeypatch):
    calls = _mock_get(
        monkeypatch,
        {
            "events": [
                {"year": 1969, "text": "Apollo 11 lands on the Moon"},
                {"year": 1945, "text": "World War II ends"},
                {"year": 1957, "text": "Sputnik 1 is launched"},
            ]
        },
    )

    events = WikipediaOnThisDayTool().fetch(date(2024, 7, 20))

    # URL is built from the target month/day, with a bot user agent and timeout.
    assert calls[0]["url"] == ("https://en.wikipedia.org/api/rest_v1/feed/onthisday/events/7/20")
    assert calls[0]["headers"]["User-Agent"] == "WikiOnThisDayBot/1.0"
    assert calls[0]["timeout"] == 10

    # Every event is date-associated with the requested month/day.
    assert [e["date"] for e in events] == [
        "1945-7-20",
        "1957-7-20",
        "1969-7-20",
    ]
    assert [e["text"] for e in events] == [
        "World War II ends",
        "Sputnik 1 is launched",
        "Apollo 11 lands on the Moon",
    ]
    # sort_key carries the year so ordering survives the date rewrite above.
    assert [e["sort_key"] for e in events] == [1945, 1957, 1969]


def test_fetch_handles_month_and_day_without_zero_padding(monkeypatch):
    calls = _mock_get(monkeypatch, {"events": []})

    WikipediaOnThisDayTool().fetch(date(2024, 1, 5))

    assert calls[0]["url"].endswith("/events/1/5")


def test_fetch_returns_empty_list_when_no_events(monkeypatch):
    _mock_get(monkeypatch, {"events": []})
    assert WikipediaOnThisDayTool().fetch(date(2024, 7, 20)) == []


def test_fetch_wraps_network_errors(monkeypatch):
    _mock_get(monkeypatch, side_effect=requests.ConnectionError("dns failure"))
    with pytest.raises(RuntimeError, match="Wikipedia fetch failed"):
        WikipediaOnThisDayTool().fetch(date(2024, 7, 20))


def test_fetch_wraps_http_errors(monkeypatch):
    class _Erroring:
        def raise_for_status(self):
            raise requests.HTTPError("503 Server Error")

    monkeypatch.setattr("tools.wikipedia.requests.get", lambda **_: _Erroring())
    with pytest.raises(RuntimeError, match="Wikipedia fetch failed"):
        WikipediaOnThisDayTool().fetch(date(2024, 7, 20))


def test_fetch_wraps_malformed_payload(monkeypatch):
    # Missing "year" would be a KeyError if it were not wrapped.
    _mock_get(monkeypatch, {"events": [{"text": "no year here"}]})
    with pytest.raises(RuntimeError, match="Wikipedia fetch failed"):
        WikipediaOnThisDayTool().fetch(date(2024, 7, 20))
