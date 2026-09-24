# Market Advisor evaluation — 24 September 2026

## Method and scope

Ten executive questions were sent to the local `market-advisor` AgentOS REST endpoint, each in a new session. The runtime model was `gpt-5.6`; the [Dubai](../evidence/dubai.md) and [Abu Dhabi](../evidence/abu_dhabi.md) evidence packs were checked on 23 September 2026. All ten runs completed with HTTP 200. They used **50,971 input tokens, 8,090 output tokens, 165.4 seconds of model duration, and no web-tool calls**. Two follow-up runs used another 10,283 input and 1,925 output tokens. These are observed usage figures, not a monetary cost estimate.

This evaluation checks answer structure, scope, citation fidelity, and stated uncertainty. It does not validate actual sales, rent, demand, permit approval, or the continuing accuracy of linked pages. The zero-tool-call result shows the speed benefit of the pack, while leaving fresh-search behavior untested. Carrying both packs also cost about 5,100 input tokens per question; trim or retrieve selectively if usage grows.

**Worked well:** all ten answers were structured and city-specific, with source links and explicit site-data gaps. **Failed or uncertain:** one citation URL drifted, one numeric decision cutoff was invented, and no unit economics or real customer demand was available. **Improve next:** validate output URLs deterministically, obtain site and recipe-cost data, and use live search only for missing or stale facts to control API usage.

| # | Executive question actually run | Observed result and source support | Finding / improvement | Seconds |
|---|---|---|---|---:|
| 1 | Which Dubai areas fit a mid-priced pizza and kebab branch, and what tradeoffs remain? | Shortlisted JLT and JVC, with Business Bay and Marina alternatives; cited Visit Dubai area material. | **Partial:** rent, footfall, and order density were correctly left unknown. Treat “mixed-use” and office demand as site hypotheses until measured. | 13.3 |
| 2 | Which Abu Dhabi areas fit the same concept? | Compared Al Reem, Khalidiyah, Khalifa City, and Shakhbout City with the Abu Dhabi Residents Office guide. | **Partial:** good area tradeoffs; possible lower occupancy cost and weaker walk-in trade in suburban sites still need quotes and counts. | 11.4 |
| 3 | Who are the direct and indirect Dubai competitors, and how should we position against them? | Named Al Mallah, Papa Johns, and Pitfire, linked menus/listings, and proposed a Jordanian meat-pizza plus kebab position. | **Useful:** categories and prices were bounded to observed examples. Map actual rivals around a candidate unit before claiming competitive advantage. | 17.6 |
| 4 | Who are the direct and indirect Abu Dhabi competitors, and how should we position against them? | Named Shawarma Planet, BBQ Shawarma, Healthy Way, and Papa Johns; cited listings, menu, and store locator. | **Useful:** product overlap was shown, not popularity. Confirm each competitor inside the final branch's delivery area. | 8.9 |
| 5 | How should the menu, portions, and localization differ by city? | Proposed individual meals in Dubai and more visible family bundles in Abu Dhabi, with bilingual descriptions and portion choices. | **Partial:** the “80% common / 20% city-specific” rule and taste/occasion assumptions were not measured. Pilot the same core menu in both catchments. | 23.2 |
| 6 | What AED price bands make sense by product and channel in each city? | Gave AED tables and cited Al Mallah, Papa Johns, Pitfire, and Abu Dhabi listings. | **Failed citation fidelity:** one Healthy Way URL was not in the pack and no web search ran. Bundle prices and a 10–15% app uplift were too precise without costs. Keep uncosted products provisional and verify every cited URL. | 15.9 |
| 7 | What launch marketing, messaging, channels, and partnerships work in each city? | Gave a six-week sequence, city messages, paid and local channels, partner types, and UAE creator-permit caveat. | **Partial:** it proposed comparing 30-day repeat rate after a two-week test, which needs a longer observation window. Measure two-week acquisition first, then 30-day repeat later. | 27.9 |
| 8 | What operations and staffing choices differ by city? | Compared urban delivery and suburban family formats, shift roles, Dubai PIC supervision, and Abu Dhabi authority checks. | **Partial:** staffing and production patterns are planning hypotheses. Confirm hours, throughput, labor cost, and current local training rules. | 17.7 |
| 9 | How should delivery platforms and licensing basics affect each branch plan? | Connected delivery reach, fees, kitchen layout, and lease decisions; cited Talabat, Dubai Municipality, ADDED, and ADAFSA. | **Useful but conditional:** fee rates, exact permits, and site approval remain unknown. Obtain written platform terms and authority/site advice before signing. | 17.3 |
| 10 | Which city should open first if budget and actual rent quotes are still unknown? | Provisionally chose Abu Dhabi/Al Reem and acknowledged missing unit economics. | **Failed decision precision:** it invented a 15% occupancy-cost cutoff. A decision gate must be qualitative until comparable quotes and an order forecast exist. | 12.1 |

## Follow-up on the two failures

- The prompt was tightened to reject invented numeric decision cutoffs and to ask for exact source URLs. Re-running **question 10** removed the 15% cutoff and kept the choice conditional on comparable site economics (HTTP 200, 10.2 seconds, no tools).
- Re-running **question 6** left family bundles unpriced pending costing and removed the asserted 10–15% markup rule. It **still changed the Healthy Way URL** despite the stricter instruction (HTTP 200, 22.4 seconds, no tools). This remains open; the next reliability improvement is a deterministic check that every answer URL is present in the evidence pack or in a live tool result. Do not treat a prompt instruction alone as that check.

## Offline check and next evaluation

An import check inside `agentos-api` confirmed that both city packs and all eight topic headings load into `INSTRUCTIONS`: `PASS: both city packs and all eight headings loaded`.

For the next round, verify every cited URL, compare the advisor with fresh official/menu pages, test a missing-evidence question that should trigger web search, and repeat the price and city-order questions after any fix. Price bands and the opening sequence must remain hypotheses until recipe costs, lease quotes, delivery contracts, and customer tests are available.
