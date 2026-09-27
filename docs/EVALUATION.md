# AI Evaluation

This report keeps three evaluation snapshots: the pack-first baseline, the first live-search round, and the latest Luna run. Citation checks verify approved domains and URL provenance; they do not prove that each source supports every claim.

## Pack-first baseline — 24 September 2026

Ten separate REST runs used `gpt-5.6` and dated Dubai/Abu Dhabi evidence packs. All completed (HTTP 200), using 50,971 input tokens, 8,090 output tokens, and 165.4 seconds. No web calls ran. The packs added about 5,100 input tokens per question and could not verify current facts.

| # | Executive question | Observed result | Finding | Seconds |
|---|---|---|---|---:|
| 1 | Which Dubai areas fit the restaurant? | Shortlisted JLT and JVC, with other alternatives. | Rent, footfall, and demand need site data. | 13.3 |
| 2 | Which Abu Dhabi areas fit? | Compared Al Reem, Khalidiyah, Khalifa, and Shakhbout City. | Verify occupancy costs and walk-in traffic. | 11.4 |
| 3 | Who are Dubai competitors? | Named Al Mallah, Papa Johns, and Pitfire. | Examples show overlap, not competitive advantage. | 17.6 |
| 4 | Who are Abu Dhabi competitors? | Named Shawarma Planet, BBQ Shawarma, Healthy Way, and Papa Johns. | Verify competitors in the final delivery area. | 8.9 |
| 5 | How should menu and localization differ? | Suggested individual meals in Dubai and family bundles in Abu Dhabi. | 80/20 menu split and taste assumptions were untested. | 23.2 |
| 6 | What prices fit each city and channel? | Gave AED bands and competitor comparisons. | An unsupported URL and 10–15% app uplift weakened trust; cost recipes first. | 15.9 |
| 7 | Which marketing and partnerships should launch? | Proposed a six-week sequence and city-specific messages. | Two weeks cannot measure 30-day repeat; measure each over its own window. | 27.9 |
| 8 | What operations and staffing differ? | Suggested roles, shift patterns, and local checks. | Staffing and production need site and authority validation. | 17.7 |
| 9 | How do delivery and licensing affect the plan? | Connected platform fees, kitchen layout, lease, and approvals. | Fees, permits, and site approval were unverified. | 17.3 |
| 10 | Which city should open first without quotes? | Provisionally chose Abu Dhabi / Al Reem. | The 15% occupancy cutoff was invented; wait for comparable economics. | 12.1 |

Follow-up runs removed the invented cutoff and uncosted price uplift, but the model still changed one menu URL. This prompted a deterministic citation check.

## First live-search round — 27 September 2026

Eight separate topic prompts used `gpt-5.6`, OpenAI Responses `web_search`, and the then-approved 13 domains. Search ran in all cases; two final answers had no native citation metadata. The strict URL-match guard retained only one answer. Parser fixes addressed tracking parameters, Markdown punctuation, and encoded parentheses; prompt changes requested inline citations and removed separate source lists.

| Topic and city | Native citations | Visible result | Seconds |
|---|---:|---|---:|
| Location / area, Dubai | 9 | Withheld: two answer URLs lacked matching native citations | 49.4 |
| Competitors, Abu Dhabi | 6 | Returned: six inline URLs matched native citations | 36.6 |
| Menu strategy, Dubai | 0 | Withheld: no native citations | 32.0 |
| Price range, Abu Dhabi | 7 | Withheld: one answer URL lacked a matching citation | 22.3 |
| Marketing, both cities | 0 | Withheld: no native citations | 58.9 |
| Delivery platforms, both cities | 4 | Withheld: answer URLs failed matching, including Markdown punctuation | 43.8 |
| Licensing, Dubai | 11 | Withheld: legal URL formatting differed and one extra page was uncited | 69.2 |
| Staffing, Abu Dhabi | 6 | Withheld: four answer URLs lacked matching citations | 48.4 |

The run used 303,482 input and 20,758 output tokens (324,240 total). The two zero-citation answers had two and six completed search calls, respectively, but no citation annotations or source arrays. Three subsequent fixes passed menu, marketing, and licensing checks; the other five could not be rerun then because the API account had no credits.

## Luna and current guard — 27 September 2026

The first eight-topic Luna round used `gpt-6-luna` with low reasoning and the expanded 25-domain allowlist. All eight answers passed the strict guard, with 36 approved-domain citations. One cited Bayut listing was titled “Ideal for Clinic,” so the answer’s F&B-approved rent claim still needed page review. Licensing details also need human review.

The guard now accepts answer links on approved domains even when native citation metadata is missing or points to another page; it adds a warning to verify those links. It still withholds off-domain links and answers that have neither an approved citation nor an approved-domain link. The focused citation and streaming suite passed **14 tests**, including the relaxed cases and off-domain rejection.

The repeated eight-topic REST run used fresh sessions and the same Luna settings. All returned HTTP 200 and `COMPLETED`; all 37 native citation URLs were approved. None needed the warning. Usage was **154,864 input tokens, 6,450 output tokens, 161,314 total, and 88.5 seconds**. These figures are not a cost estimate.

| Topic and city | Native citations | Guard result | Seconds |
|---|---:|---|---:|
| Location / area, Dubai | 3 | Returned; one rent-use claim needs source review | 9.2 |
| Competitors, Abu Dhabi | 4 | Returned | 7.9 |
| Menu strategy, Dubai | 2 | Returned | 11.2 |
| Price range, Abu Dhabi | 2 | Returned | 6.5 |
| Marketing, both cities | 2 | Returned | 6.0 |
| Delivery platforms, both cities | 9 | Returned | 18.6 |
| Licensing, Dubai | 11 | Returned; legal details need human review | 12.0 |
| Staffing, Abu Dhabi | 3 | Returned; roster is an estimate | 13.0 |

## Limits

The approved sources do not establish a specific unit’s final rent, measured footfall, order density, delivery commission, or a defensible staffing count. URL checks establish domain and citation provenance, not claim accuracy or demand. Validate site economics, current legal requirements, platform terms, and customer response before committing.
