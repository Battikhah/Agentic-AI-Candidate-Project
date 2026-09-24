"""Check that the advisor never presents an unsupported citation URL as evidence."""

import json
import unittest
from types import SimpleNamespace

from agno.run.agent import RunOutput

from agents.market_advisor import EVIDENCE_URLS, check_citation_urls


class CitationUrlTest(unittest.TestCase):
    """Cover evidence-pack, live-search, and invented-link answers."""

    def test_citation_sources(self) -> None:
        pack_url = next(iter(EVIDENCE_URLS))
        supported = RunOutput(content=f"[Source]({pack_url})")
        check_citation_urls(supported)
        self.assertEqual(supported.content, f"[Source]({pack_url})")

        live_url = "https://example.com/current-menu"
        tool = SimpleNamespace(tool_name="web_fetch", result=json.dumps({
            "results": [{"url": "https://example.com/category", "excerpts": [f"[menu]({live_url})"]}]
        }))
        live = RunOutput(content=f"[Source]({live_url})", tools=[tool])
        check_citation_urls(live)
        self.assertEqual(live.content, f"[Source]({live_url})")

        category = RunOutput(content="[Category](https://example.com/category)", tools=[tool])
        check_citation_urls(category)
        self.assertEqual(category.content, "[Category](https://example.com/category)")

        for name in ("parallel_search", "parallel_extract"):
            sdk_tool = SimpleNamespace(tool_name=name, result=tool.result)
            sdk_live = RunOutput(content=f"[Source]({live_url})", tools=[sdk_tool])
            check_citation_urls(sdk_live)
            self.assertEqual(sdk_live.content, f"[Source]({live_url})")

        invented = RunOutput(content="[Source](https://example.invalid/invented)", tools=[tool])
        check_citation_urls(invented)
        self.assertNotIn("example.invalid", invented.content)
        self.assertIn("could not verify", invented.content)

        malformed = RunOutput(content="[Source](https://example.invalid/invented)", tools=[
            SimpleNamespace(tool_name="web_search", result=json.dumps({"results": None}))
        ])
        check_citation_urls(malformed)
        self.assertIn("could not verify", malformed.content)


if __name__ == "__main__":
    unittest.main()
