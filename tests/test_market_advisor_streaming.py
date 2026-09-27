"""Protect advisor requests from leaking text before the citation hook runs."""

import unittest
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from app.main import market_advisor_streaming_guard


class MarketAdvisorStreamingGuardTest(unittest.TestCase):
    """Exercise the route guard without invoking an agent or model."""

    def setUp(self) -> None:
        self.app = FastAPI()
        self.app.middleware("http")(market_advisor_streaming_guard)
        self.advisor_calls = 0

        @self.app.post("/agents/market-advisor/runs")
        async def advisor(request: Request):
            self.advisor_calls += 1
            form = await request.form()
            return {"message": form.get("message")}

        @self.app.post("/agents/other-agent/runs")
        async def other_agent():
            return {"ok": True}

        self.client = TestClient(self.app)

    def test_missing_or_true_stream_is_rejected_but_false_preserves_body(self) -> None:
        invalid_forms = (
            {"message": "hello"},
            {"message": "hello", "stream": "true"},
            {"message": "hello", "stream": "sometimes"},
        )
        for data in invalid_forms:
            with self.subTest(data=data):
                response = self.client.post("/agents/market-advisor/runs", data=data)
                self.assertEqual(response.status_code, 400)

        duplicate = self.client.post(
            "/agents/market-advisor/runs",
            content=urlencode([("message", "hello"), ("stream", "false"), ("stream", "false")]),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(duplicate.status_code, 400)

        response = self.client.post(
            "/agents/market-advisor/runs", data={"message": "keep this", "stream": "false"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"message": "keep this"})

    def test_oversized_request_is_rejected_before_downstream(self) -> None:
        response = self.client.post(
            "/agents/market-advisor/runs",
            data={"message": "x" * (64 * 1024), "stream": "false"},
        )
        self.assertEqual(response.status_code, 413)
        self.assertEqual(self.advisor_calls, 0)

    def test_other_agent_stream_request_is_unchanged(self) -> None:
        response = self.client.post("/agents/other-agent/runs", data={"stream": "true"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"ok": True})


if __name__ == "__main__":
    unittest.main()
