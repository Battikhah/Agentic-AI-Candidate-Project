"""Protect advisor requests from leaking text before the citation hook runs."""

import unittest
import json
from urllib.parse import urlencode

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from fastapi.responses import StreamingResponse

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
            if form.get("stream") != "false":
                async def events():
                    yield self._event("RunStarted", {"run_id": "run-1"})
                    if form.get("message") == "safe":
                        yield self._event("RunContent", {"run_id": "run-1", "content": "Checked "})
                        yield self._event("RunContent", {"run_id": "run-1", "content": "answer"})
                        yield self._event("RunContentCompleted", {"run_id": "run-1"})
                        yield self._event("RunCompleted", {"run_id": "run-1", "content": "Checked answer"})
                        return
                    if form.get("message") == "partial":
                        yield self._event("RunContent", {"run_id": "run-1", "content": "Unchecked https://evil.invalid"})
                        yield self._event("RunError", {"run_id": "run-1", "content": "Run failed."})
                        return
                    yield self._event("RunContent", {"run_id": "run-1", "content": "Unchecked https://evil.invalid"})
                    yield self._event("RunContentCompleted", {"run_id": "run-1"})
                    yield self._event(
                        "RunCompleted",
                        {
                            "run_id": "run-1",
                            "content": "I could not verify this answer.",
                            "citations": {"urls": [{"url": "https://evil.invalid/source"}]},
                        },
                    )

                return StreamingResponse(events(), media_type="text/event-stream")
            return {"message": form.get("message")}

        self.client = TestClient(self.app)

    @staticmethod
    def _event(name: str, payload: dict[str, str]) -> bytes:
        return f"event: {name}\ndata: {json.dumps({'event': name, **payload})}\n\n".encode()

    def test_streaming_ui_gets_only_post_hook_checked_content(self) -> None:
        response = self.client.post("/agents/market-advisor/runs", data={"message": "hello", "stream": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")
        self.assertNotIn("evil.invalid", response.text)
        self.assertIn("I could not verify this answer.", response.text)
        self.assertIn("event: RunContent", response.text)

    def test_missing_stream_uses_agno_streaming_default(self) -> None:
        response = self.client.post("/agents/market-advisor/runs", data={"message": "hello"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/event-stream; charset=utf-8")

    def test_checked_stream_replays_original_content_events(self) -> None:
        response = self.client.post("/agents/market-advisor/runs", data={"message": "safe", "stream": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text.count('"content": "Checked '), 2)
        self.assertIn('"content": "answer"', response.text)

    def test_incomplete_stream_does_not_expose_unchecked_content(self) -> None:
        response = self.client.post("/agents/market-advisor/runs", data={"message": "partial", "stream": "true"})

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("evil.invalid", response.text)
        self.assertIn("Run failed.", response.text)

    def test_duplicate_or_invalid_stream_fields_are_rejected(self) -> None:
        duplicate = self.client.post(
            "/agents/market-advisor/runs",
            content=urlencode([("message", "hello"), ("stream", "false"), ("stream", "false")]),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        self.assertEqual(duplicate.status_code, 400)
        invalid = self.client.post("/agents/market-advisor/runs", data={"message": "hello", "stream": "sometimes"})
        self.assertEqual(invalid.status_code, 400)

    def test_non_streaming_request_preserves_json_response(self) -> None:
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

if __name__ == "__main__":
    unittest.main()
