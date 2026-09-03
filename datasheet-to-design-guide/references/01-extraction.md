# Requirement extraction

Use one record per candidate requirement.

```text
ID: temporary extraction ID
Class: A | B | C | D | E | F | G
Statement: normalized engineering requirement
Strength: REQUIRED | RECOMMENDED | APP | INFORMATIONAL | UNCLEAR
Condition: exact operating/test/mode/temperature/supply condition
Value/Range: numerical limit or N/A
Units: explicit units or N/A
Applies to: pin/net/component/package/mode/layout region
Source location: PDF page + section/table/figure/note
Anchor: short verbatim source text
Verification: netlist | schematic | bom | project_context | calculation | pcb | simulation | measurement | manual
Required facts: abstract future DesignFacts needed to evaluate this rule
Required evidence: evidence classes needed to establish those facts
Dependency keys: design properties whose change must reopen the rule
Depends on rules: stable checklist IDs if this result semantically depends on another rule
Open question: none or explicit unresolved issue
```

## Extraction rules

- Preserve inequalities exactly: `<`, `≤`, typical, minimum and maximum are not interchangeable.
- Preserve RMS/peak/peak-to-peak, differential/common-mode, DC/AC, source/sink and input/output distinctions.
- When a table value is conditioned by a note, the note is part of the same record.
- When an equation has a validity range, extract the equation and validity range together.
- Pin descriptions can contain constraints not repeated elsewhere; scan every used pin.
- Typical application schematics are evidence of topology but not automatically a mandatory device requirement. Use `APP` when an application-design constraint is useful for review but intentionally distinct from the component specification.
- Layout recommendations that use words such as `place close`, `minimize loop`, `keep out`, `do not route`, or explicit distance/area rules should become checklist candidates.
- Required facts and dependency keys describe the future design-review interface; they are not permission to invent current design values.

## Hidden-constraint pass

After normal extraction, deliberately search again for:

- notes and footnotes attached to electrical tables;
- prose immediately before/after equations;
- source impedance or external-network current restrictions;
- input clamp/protection current limits;
- startup and power-sequencing caveats;
- conditions under which stated accuracy/specifications are valid;
- common-mode restrictions that coexist with differential input limits;
- output load/capacitance restrictions;
- decoupling ESR/value/location requirements;
- thermal derating and package-specific restrictions;
- isolation working-voltage vs transient/surge distinctions;
- PCB keepout, creepage and clearance notes;
- `not tested`, `not production tested`, `guaranteed by design` qualifiers.
