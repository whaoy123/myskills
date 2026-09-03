# Output format

A completed extraction produces four mutually consistent files:

```text
<part-number>/
├── usage-guide.md
├── checklist.md
├── PROVENANCE.md
└── module.yaml
```

## usage-guide.md

Keep it compact and task-oriented. Each section should contain only design-relevant facts, formulas, decisions and boundaries. Do not duplicate the full checklist.

## checklist.md

Use stable IDs by domain: `PWR-xx`, `IN-xx`, `OUT-xx`, `EXT-xx`, `FUNC-xx`, `SAFE-xx`, `PCB-xx`, `SPEC-xx`.

Preferred row format:

| ID | Strength | Requirement | Condition | Source | Applies to | Verification | Status |
|---|---|---|---|---|---|---|---|
| IN-01 | REQUIRED | ... | ... | p.xx / Table x / Note y | R1, R2, INP | calculation | UNVERIFIED |

Strength values: `REQUIRED`, `RECOMMENDED`, `APP`, `INFORMATIONAL`, `UNCLEAR`.

`APP` is for a manufacturer's application design/example that is intentionally not classified as a universal component specification.

Initial source-module status is normally `UNVERIFIED`. Concrete review states (`PASS`, `FAIL`, `N/A`, `UNCLEAR`) are owned by `hardware-design-review`; do not destructively rewrite the source checklist after every board review.

## PROVENANCE.md

Record source file, manufacturer, exact device/variant, datasheet revision/date, extraction date, package/mode scope, unreadable sections, validation method, application-vs-specification decisions, unresolved ambiguities, and later checklist additions.

## module.yaml

Follow `04-module-interface.md`. It contains module identity/version, conservative selectors, capabilities, companion-file paths, checklist rule IDs, verification methods, required fact/evidence declarations, invalidation dependency keys, and rule dependencies. It should not duplicate the full requirement prose or numeric datasheet corpus.
