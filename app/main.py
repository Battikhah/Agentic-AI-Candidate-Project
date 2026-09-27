"""AgentOS application for the UAE Market Advisor."""

import json
import re
from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.os.config import AuthorizationConfig
from fastapi import Request
from fastapi.responses import JSONResponse, Response

from agents.market_advisor import market_advisor
from db import get_postgres_db

agent_os = AgentOS(
    name="UAE Market Advisor",
    tracing=True,
    scheduler=False,
    authorization=getenv("RUNTIME_ENV", "prd") != "dev",
    authorization_config=AuthorizationConfig(user_isolation=True),
    db=get_postgres_db(),
    agents=[market_advisor],
    config=str(Path(__file__).parent / "config.yaml"),
)
app = agent_os.get_app()

MAX_MARKET_ADVISOR_REQUEST_BYTES = 64 * 1024
CONTENT_EVENTS = {"RunContent", "RunContentCompleted", "RunIntermediateContent"}


def _parse_sse_event(frame: bytes) -> tuple[str | None, dict | None]:
    """Read one Agno SSE frame while preserving the original bytes for replay."""
    lines = frame.decode("utf-8", errors="replace").splitlines()
    event = next((line[7:] for line in lines if line.startswith("event: ")), None)
    data = "\n".join(line[6:] for line in lines if line.startswith("data: "))
    try:
        payload = json.loads(data) if data else None
    except json.JSONDecodeError:
        payload = None
    if event is None and isinstance(payload, dict):
        event = payload.get("event")
    return event, payload if isinstance(payload, dict) else None


def _format_sse_event(event: str, payload: dict) -> bytes:
    payload["event"] = event
    return f"event: {event}\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()


def _checked_sse_body(body: bytes) -> bytes:
    """Replay only final content that has passed the advisor's post-hook."""
    frames = [frame for frame in re.split(rb"\r?\n\r?\n", body) if frame]
    parsed = [_parse_sse_event(frame) for frame in frames]
    completed_index = next(
        (index for index in range(len(frames) - 1, -1, -1) if parsed[index][0] == "RunCompleted"),
        None,
    )
    if completed_index is None:
        return b"\n\n".join(
            frame for frame, (event, _) in zip(frames, parsed) if event not in CONTENT_EVENTS
        ) + b"\n\n"

    final_payload = parsed[completed_index][1]
    final_content = final_payload.get("content") if final_payload else None
    content_parts = [
        payload.get("content")
        for event, payload in parsed
        if event == "RunContent" and payload is not None
    ]
    if isinstance(final_content, str) and all(isinstance(part, str) for part in content_parts):
        if "".join(content_parts) == final_content:
            return b"\n\n".join(
                frame for frame, (event, _) in zip(frames, parsed) if event != "RunIntermediateContent"
            ) + b"\n\n"

    # The post-hook changed the answer; discard streamed deltas and expose only its checked result.
    safe_payload = dict(final_payload or {})
    safe_payload["citations"] = None
    safe_payload["references"] = None
    replacement = _format_sse_event("RunContent", safe_payload)
    completion = next(
        (frame for frame, (event, _) in zip(frames, parsed) if event == "RunContentCompleted"),
        _format_sse_event("RunContentCompleted", {key: safe_payload[key] for key in ("run_id", "session_id") if key in safe_payload}),
    )
    output = []
    for index, (frame, (event, _)) in enumerate(zip(frames, parsed)):
        if event in CONTENT_EVENTS:
            continue
        if index == completed_index:
            output.extend((replacement.rstrip(b"\n"), completion.rstrip(b"\n")))
        if event == "RunCompleted":
            frame = _format_sse_event(event, safe_payload).rstrip(b"\n")
        output.append(frame)
    return b"\n\n".join(output) + b"\n\n"


async def market_advisor_streaming_guard(request: Request, call_next):
    """Buffer advisor streams until citation checks finish, and bound every request."""
    if request.method != "POST" or request.scope.get("path") != "/agents/market-advisor/runs":
        return await call_next(request)

    content_length = request.headers.get("content-length")
    try:
        declared_length = int(content_length) if content_length is not None else None
    except ValueError:
        declared_length = None
    if declared_length is None or declared_length < 0:
        return JSONResponse(
            {"detail": "Market advisor requests require Content-Length and stream=false."},
            status_code=400,
        )
    if declared_length > MAX_MARKET_ADVISOR_REQUEST_BYTES:
        return JSONResponse(
            {"detail": "Market advisor requests are limited to 64 KiB; use stream=false."},
            status_code=413,
        )

    body = await request.body()
    if len(body) != declared_length or len(body) > MAX_MARKET_ADVISOR_REQUEST_BYTES:
        return JSONResponse({"detail": "Invalid or oversized market advisor request body."}, status_code=400)

    try:
        form = await request.form()
    except Exception:
        return JSONResponse(
            {"detail": "Market advisor requests require a valid form with stream=false."},
            status_code=400,
        )
    stream_values = form.getlist("stream")
    if len(stream_values) > 1 or (
        stream_values
        and (not isinstance(stream_values[0], str) or stream_values[0].strip().casefold() not in {"false", "true"})
    ):
        return JSONResponse(
            {"detail": "Market advisor requests accept one stream field with value true or false."},
            status_code=400,
        )

    response = await call_next(request)
    streaming = not stream_values or stream_values[0].strip().casefold() == "true"
    if not streaming or not response.headers.get("content-type", "").startswith("text/event-stream"):
        return response

    # ponytail: Buffer the short advisor response in memory so no text reaches the UI before citation validation.
    body = b"".join([chunk async for chunk in response.body_iterator])
    headers = {
        key: value
        for key, value in response.headers.items()
        if key.lower() not in {"content-length", "content-type", "transfer-encoding"}
    }
    return Response(
        content=_checked_sse_body(body),
        status_code=response.status_code,
        headers=headers,
        media_type="text/event-stream",
        background=response.background,
    )


app.middleware("http")(market_advisor_streaming_guard)


if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=False)
