# Output format

## usage-guide.md

Keep it compact and task-oriented. Each section should contain only design-relevant facts, formulas, decisions and boundaries.

For a quantitative rule, prefer:

```text
Requirement: ...
Condition: ...
Source: p.xx, Table/Figure/Section ...
Design consequence: ...
```

Do not duplicate the full checklist.

## checklist.md

Use stable IDs by domain:

- `PWR-xx` power/ground/startup
- `IN-xx` input/front-end
- `OUT-xx` output/load
- `EXT-xx` external components/calculations
- `FUNC-xx` functional/timing/control
- `SAFE-xx` absolute max/protection/isolation/thermal
- `PCB-xx` layout/routing/decoupling
- `SPEC-xx` conditions needed to achieve stated performance

Recommended row format:

| ID | Requirement | Condition | Source | Applies to | Verification | Status |
|---|---|---|---|---|---|---|
| IN-01 | ... | ... | p.xx / Table x / Note y | R1, R2, INP | calculation | UNVERIFIED |

Below a row, add dependencies only when needed:

```text
Dependencies: changing R1 reopens IN-01, IN-03, SAFE-02 and SPEC-04.
```

Status values:

- `UNVERIFIED`
- `PASS`
- `FAIL`
- `N/A`
- `UNCLEAR`

## PROVENANCE.md

Record:

- source file name;
- exact device and variant;
- datasheet revision/date;
- extraction date;
- package/mode assumed;
- any unreadable/missing sections;
- validation method and reviewer/model when known;
- later checklist additions and why they were added.
