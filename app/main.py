"""AgentOS application for the UAE Market Advisor."""

from os import getenv
from pathlib import Path

from agno.os import AgentOS
from agno.os.config import AuthorizationConfig
from fastapi import Request
from fastapi.responses import JSONResponse

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


async def market_advisor_streaming_guard(request: Request, call_next):
    """Require bounded, non-streaming advisor runs so citation checks finish first."""
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
    if (
        len(stream_values) != 1
        or not isinstance(stream_values[0], str)
        or stream_values[0].strip().casefold() != "false"
    ):
        return JSONResponse(
            {"detail": "Market advisor streaming is disabled; submit exactly one form field: stream=false."},
            status_code=400,
        )

    return await call_next(request)


app.middleware("http")(market_advisor_streaming_guard)


if __name__ == "__main__":
    agent_os.serve(app="app.main:app", reload=False)
