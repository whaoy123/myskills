# Validation

Validation is a second pass, not a continuation of extraction.

## Per-item gates

1. **Anchor gate** — Can the quoted anchor be found in the source at the stated location?
2. **Meaning gate** — Does the normalized statement say only what the source supports?
3. **Condition gate** — Are all important conditions, notes, units and qualifiers attached?
4. **Applicability gate** — Does it apply to this exact device/variant/package/mode?
5. **Conflict gate** — Is there a stricter or more specific requirement elsewhere?
6. **Classification gate** — Is the Strength correct: `REQUIRED`, `RECOMMENDED`, `APP`, `INFORMATIONAL`, or `UNCLEAR`? Application guidance must not be silently promoted to component specification.
7. **Actionability gate** — If it affects design, can a reviewer identify what object to inspect and how to verify it?
8. **Interface gate** — Are the future `required_facts`, `required_evidence`, `dependency_keys`, and any `depends_on_rules` sufficient for `hardware-design-review` to execute and incrementally reopen the rule?

Any failed gate becomes `UNCLEAR` or is rejected; never repair it from generic knowledge.

## Coverage challenge

After validating existing candidates, search the source specifically for omissions. The reviewer should try to falsify the statement “the checklist is complete enough for design review.”

Prioritize:

- footnotes not represented by any checklist item;
- used pins with no extracted constraints;
- equations with no extracted validity conditions;
- recommended-operating tables with unrepresented rows relevant to the design;
- layout sections with no corresponding checklist item;
- typical-application components whose purpose is not understood;
- protection/clamp currents and source-resistance restrictions;
- performance specifications whose test conditions are not represented;
- rules that are human-readable but lack enough dependency metadata for incremental review.

Record newly found items; do not merely state that another pass was completed.
