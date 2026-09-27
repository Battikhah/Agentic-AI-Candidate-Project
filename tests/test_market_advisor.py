"""Check that the advisor never presents an unsupported citation URL as evidence."""

import unittest
from types import SimpleNamespace

from agno.run.agent import RunOutput

from agents.market_advisor import check_citation_urls


class CitationUrlTest(unittest.TestCase):
    """Cover native citations, historical pack links, and invented URLs."""

    def test_approved_domain_url_without_native_citation_is_kept_with_warning(self) -> None:
        historical_pack_url = "https://www.visitdubai.com/en/things-to-do/itineraries/jlt-foodie-trail"
        answer = RunOutput(content=f"[Source]({historical_pack_url})")

        check_citation_urls(answer)

        self.assertIn(historical_pack_url, answer.content)
        self.assertIn("native citation", answer.content)
        self.assertIn("verify", answer.content.lower())

    def test_factual_answer_without_native_citations_is_rejected(self) -> None:
        answer = RunOutput(content="JLT rents are currently AED 200,000 per year.")

        check_citation_urls(answer)

        self.assertIn("could not verify", answer.content)

    def test_citation_sources(self) -> None:
        live_url = "https://talabat.com/uae/restaurant/current-menu"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=live_url)])
        live = RunOutput(content=f"[Source]({live_url})", citations=citations)
        check_citation_urls(live)
        self.assertEqual(live.content, f"[Source]({live_url})")

        invented = RunOutput(content="[Source](https://example.invalid/invented)")
        check_citation_urls(invented)
        self.assertNotIn("example.invalid", invented.content)
        self.assertIn("could not verify", invented.content)

    def test_live_search_citation_must_use_an_approved_domain(self) -> None:
        off_allowlist_url = "https://talabat.com.evil.org/current-market-report"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=off_allowlist_url)])
        metadata = SimpleNamespace(tool_name="web_search", result=off_allowlist_url)
        answer = RunOutput(content=f"[Market report]({off_allowlist_url})", citations=citations, tools=[metadata])

        check_citation_urls(answer)

        self.assertIn("could not verify", answer.content)

    def test_native_search_citation_allows_configured_domain_outside_evidence_pack(self) -> None:
        live_url = "https://talabat.com/uae/restaurant/current-listing"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=live_url)])
        answer = RunOutput(content=f"[Current listing]({live_url})", citations=citations)

        check_citation_urls(answer)

        self.assertEqual(answer.content, f"[Current listing]({live_url})")

    def test_openai_tracking_parameter_matches_canonical_answer_url(self) -> None:
        canonical_url = "https://talabat.com/uae/restaurant/current-menu?location=jlt"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=f"{canonical_url}&utm_source=openai")])
        answer = RunOutput(content=f"[Current menu]({canonical_url})", citations=citations)

        check_citation_urls(answer)

        self.assertEqual(answer.content, f"[Current menu]({canonical_url})")

    def test_markdown_backticks_do_not_change_citation_url(self) -> None:
        cited_url = "https://talabat.com/uae/restaurant/current-menu"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=cited_url)])
        answer = RunOutput(content=f"See `{cited_url}` for the current menu.", citations=citations)

        check_citation_urls(answer)

        self.assertEqual(answer.content, f"See `{cited_url}` for the current menu.")

    def test_parenthesized_citation_url_survives_markdown_link(self) -> None:
        cited_url = "https://dlp.dubai.gov.ae/legislation/Resolution%20(13)%20of%202024.html"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=cited_url)])
        answer = RunOutput(content=f"[Dubai rule]({cited_url})", citations=citations)

        check_citation_urls(answer)

        self.assertEqual(answer.content, f"[Dubai rule]({cited_url})")

    def test_encoded_citation_parentheses_match_literal_answer_url(self) -> None:
        cited_url = "https://dlp.dubai.gov.ae/legislation/Resolution%20%2813%29%20of%202024.html"
        answer_url = "https://dlp.dubai.gov.ae/legislation/Resolution%20(13)%20of%202024.html"
        citations = SimpleNamespace(urls=[SimpleNamespace(url=cited_url)])
        answer = RunOutput(content=f"[Dubai rule]({answer_url})", citations=citations)

        check_citation_urls(answer)

        self.assertEqual(answer.content, f"[Dubai rule]({answer_url})")

    def test_unmatched_url_on_an_approved_domain_is_kept_with_warning(self) -> None:
        citations = SimpleNamespace(urls=[SimpleNamespace(url="https://talabat.com/uae/restaurant/current-menu")])
        unrelated_url = "https://talabat.com/uae/restaurant/another-menu"
        answer = RunOutput(content=f"[Other menu]({unrelated_url})", citations=citations)

        check_citation_urls(answer)

        self.assertIn(unrelated_url, answer.content)
        self.assertIn("native citation", answer.content)
        self.assertIn("verify", answer.content.lower())

    def test_answer_link_outside_approved_domains_is_rejected(self) -> None:
        citations = SimpleNamespace(urls=[SimpleNamespace(url="https://talabat.com/uae/restaurant/current-menu")])
        answer = RunOutput(content="[Source](https://example.invalid/menu)", citations=citations)

        check_citation_urls(answer)

        self.assertIn("could not verify", answer.content)


if __name__ == "__main__":
    unittest.main()
