# UAE Market Advisor

This repository contains one product: a live, source-grounded advisor for restaurants assessing expansion into Dubai and Abu Dhabi.

- The agent prompt, approved domains, and citation checks are in `agents/market_advisor.py`.
- AgentOS registration and the non-streaming request guard are in `app/main.py`.
- PostgreSQL persistence is in `db/`; local services are in `compose.yaml`.
- Keep new functionality specific to the advisor. Do not restore generic AgentOS teams, agents, Studio, workflows, or schedules.
- Preserve the approved-domain restriction and reject links outside it.
- Keep the evaluation report in `docs/EVALUATION.md` and advisor tests in `tests/`.
