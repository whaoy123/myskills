# Reference Module Contract

`hardware-design-review` loads engineering knowledge as modular references. The core Skill contains no device-specific limits.

Reference classes:

```text
references/
├── devices/      exact devices/families/packages
├── interfaces/   electrical or protocol interface constraints
├── power/        regulator/DC-DC/rail/topology rules
├── isolation/    isolation-domain and safety-spacing rules
├── pcb/          reusable layout/routing/placement rules
└── system/       cross-device signal-chain/power/fault rules
```

A native module directory uses:

```text
MODULE_NAME/
├── usage-guide.md
├── checklist.md
├── PROVENANCE.md
└── module.yaml
```

For generic modules that are not derived from one datasheet, the three Markdown files still serve the same roles: engineering guidance, executable checklist, and provenance/authority/ambiguity record.

## Human vs machine interface

- `usage-guide.md`: explains how to use the device/structure correctly.
- `checklist.md`: contains stable executable rule IDs.
- `PROVENANCE.md`: says where each rule came from and records ambiguity/conditions.
- `module.yaml`: machine index. It selects the module and declares what each checklist rule depends on. It MUST NOT become a second copy of all numeric datasheet limits.

`module.yaml` is validated against `schemas/reference-module.schema.json` conceptually; `scripts/validate_module.py` performs dependency-light structural validation.

## Checklist row contract

Preferred columns:

| ID | Strength | Requirement | Condition | Source | Applies to | Verification | Status |
|---|---|---|---|---|---|---|---|

Reference publication status is normally `UNVERIFIED`. During a concrete design review it becomes `PASS`, `FAIL`, `UNCLEAR` or `N/A` in the review result; the source checklist itself does not need to be destructively edited.

Strength vocabulary:

- `REQUIRED`
- `RECOMMENDED`
- `APP` when an application example/rule is intentionally distinct from a device specification
- `INFORMATIONAL`
- `UNCLEAR`

## module.yaml principles

`module.yaml` should answer only:

1. What module is this?
2. When should it be loaded?
3. What capabilities/categories does it cover?
4. What stable checklist rules exist?
5. What facts/evidence does each rule require?
6. What design changes invalidate each result?

Do not duplicate the detailed rule text or source quotation from `checklist.md`/`PROVENANCE.md` unless a short machine condition is necessary for applicability.

See `templates/module.yaml` for the canonical shape.
