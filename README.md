# UAE Market Advisor

A live web research advisor for restaurant executives assessing expansion into Dubai and Abu Dhabi. It adapts its analysis to the restaurant concept provided and covers location, competitors, menu, pricing, marketing, delivery platforms, licensing, and staffing.

The advisor uses OpenAI's native web search, restricted to 25 approved domains. It separates sourced facts from recommendations, flags uncertainty, and checks links before returning an answer. Approved-domain links without a matching native citation stay visible with a warning; links outside the approved domains are withheld. It searches live for factual answers and does not use stored evidence packs.

## Run the demo

You need Docker Desktop and an OpenAI API key with available API credits.

```sh
cp example.env .env
# Add your key to OPENAI_API_KEY in .env
docker compose up -d --build
```

Check the API at [http://localhost:8000/docs](http://localhost:8000/docs). For the Agno control plane, connect [os.agno.com](https://os.agno.com) to the local endpoint `http://localhost:8000` and use Sessions or Traces to review saved runs.

Run the advisor in a terminal:

```sh
docker exec -e AGNO_DEBUG=False -it agentos-api python -c 'import asyncio; from agents.market_advisor import market_advisor; asyncio.run(market_advisor.acli_app())'
```

Try this prompt:

> We are planning to expand our [restaurant concept and cuisine] into the UAE. Compare Dubai and Abu Dhabi for our concept. Cover location, competitors, menu, AED price range, marketing, delivery platforms, licensing, and staffing. Give concise recommendations and tradeoffs, cite current approved sources inline, and say when rent, footfall, commissions, or staffing figures are not verified.

For direct API requests, submit `stream=false`. The citation check runs after the model completes, so the advisor endpoint rejects streaming requests.

## How it works

```text
Question → UAE Market Advisor → OpenAI Responses API + native web_search
         → 25-domain allowlist → citation URL check → answer + saved session
```

The agent and its instructions are in [`agents/market_advisor.py`](agents/market_advisor.py). AgentOS registers only this advisor in [`app/main.py`](app/main.py). PostgreSQL stores sessions and traces; [`compose.yaml`](compose.yaml) runs both services.

## Evaluation and limits

The eight-topic evaluation, citation results, and known limitations are in [`docs/EVALUATION.md`](docs/EVALUATION.md). The approved websites do not always establish exact unit rent, measured footfall, platform commissions, or a defensible staffing count. The advisor should mark these as unknown and recommend local validation. URL checks verify domain and citation alignment; they do not prove every claim is correct.

## Disclosure

I defined the project direction, advisory topics, source requirements, and handling of unsupported claims; set evaluation goals; reviewed outputs; made final implementation decisions; ran the Agno Docker platform; and prepared the demonstration. AI coding agents assisted with research, implementation, debugging, evaluation, and documentation. I understand the resulting project and can explain its design and limitations.
