# Source Quality Policy — Authority and Independence

## Why two dimensions

A source can be highly authoritative for one type of claim and still be non-independent when evaluating itself.

Do not collapse source quality into a single score.

## Authority

Authority asks:

> How direct, qualified, and technically authoritative is this source for this specific claim?

Default interpretation:

- `HIGH`: primary standard/manual/datasheet/original paper/original repository for facts it directly owns; authoritative institution; direct measurement/report.
- `MEDIUM`: reputable technical secondary source, review, textbook, independent engineering analysis.
- `LOW`: weak aggregation, anecdote, unsourced summary, discovery-only material.

Authority is claim-specific. A vendor datasheet can be HIGH for absolute maximum ratings but not necessarily for broad market superiority.

## Independence

Independence asks:

> How independent is this source from the product, method, organization, or decision being evaluated?

Default interpretation:

- `HIGH`: independent replication, third-party test, regulator/standard body, unrelated technical analysis.
- `MEDIUM`: partially independent review or community implementation with disclosed dependencies.
- `LOW`: vendor claims about its own product, authors comparing their own method, project maintainers describing their own project.
- `N/A`: independence is not meaningful for the claim, such as an official pin definition.

## Examples

| Claim | Source | Authority | Independence |
|---|---|---|---|
| Device absolute maximum voltage | vendor datasheet | HIGH | N/A/LOW |
| Device is better than competitors | same vendor marketing/app note | MEDIUM/HIGH for own measurements | LOW |
| Algorithm beats baseline | original paper | HIGH for reported experiment | LOW |
| Algorithm reproduces on another dataset | independent replication | HIGH/MEDIUM | HIGH |
| Open-source project architecture | project source/docs | HIGH | LOW |
| Common project failure mode | reproducible GitHub issue + maintainer confirmation | MEDIUM/HIGH | MEDIUM |

## Use in decisions

- Specifications: prioritize Authority.
- Comparative superiority: seek Independence.
- Pitfalls: lower-authority sources can generate a hypothesis, but important risks should be verified with stronger evidence where possible.
- Safety/feasibility blockers: prefer primary/authoritative evidence or direct engineering verification.
