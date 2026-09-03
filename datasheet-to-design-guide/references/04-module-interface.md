# module.yaml interface

`module.yaml` is the machine-readable sidecar consumed by `hardware-design-review`. Its purpose is selection and dependency mapping, not duplication of the datasheet.

Canonical shape:

```yaml
schema_version: 1
module:
  id: device:manufacturer:part-number
  type: device
  name: PART_NUMBER
  manufacturer: MANUFACTURER
  revision: DATASHEET_REVISION
selectors:
  part_numbers: [PART_NUMBER]
  aliases: []
  packages: []
  structures: []
capabilities: [connection, electrical, pcb]
files:
  usage_guide: usage-guide.md
  checklist: checklist.md
  provenance: PROVENANCE.md
rule_namespace: PART_NUMBER
rules:
  - id: PWR-01
    category: power
    strength: REQUIRED
    verification: [netlist, calculation]
    required_facts: [component.supply_voltage]
    required_evidence: [netlist, project_context]
    affects: [component.supply, power_domain]
    dependency_keys: [component.part_number, component.supply_net, net.supply_voltage]
    depends_on_rules: []
```

## Selectors

`part_numbers` and `aliases` contain only verified covered identities. `packages` narrows package-sensitive rules. `structures` is mainly for generic/non-device modules. Never broaden selectors from family similarity alone.

## Rule metadata

`required_facts` names abstract properties needed to evaluate the rule, for example `component.supply_voltage`, `pin.connected_net`, `network.resistor_values`, `pcb.component_distance`.

`required_evidence` names evidence types able to establish them, such as `netlist`, `bom`, `schematic`, `project_context`, `pcb`.

`dependency_keys` names properties whose change invalidates a previous result. The review engine instantiates them into concrete keys such as `COMPONENT:R17:value` or `PIN:U3.4:net`.

`depends_on_rules` captures semantic rule dependencies for transitive reopening.

## No duplicated authority

Do not mirror numeric limits into `module.yaml` when checklist/provenance already contain them and no typed expression engine consumes them. The first interface version intentionally keeps `module.yaml` as an index; a future schema can add typed expressions only when they can be validated automatically against provenance.
