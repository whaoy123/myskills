# Memory policy

## Decision order

1. Resolve owner before deciding whether to save.
2. Explicit save/forget requests take priority.
3. Stable, directly stated, future-useful, low-sensitivity information may auto-save.
4. Inferred or uncertain information requires confirmation.
5. Temporary, trivial, transform-only, or duplicate information is skipped.

## Auto-save examples

- “这个项目后续都不能覆盖原始 Word，只修改副本。”
- “我的最终 HiFi5 交付必须是纯 C，不依赖 Python。”
- “以后 PCB 计算默认以用户明确给出的铜厚为准。”

These are durable rules that change future work and are not merely one task's current status.

## Ask-before-save examples

- The user repeatedly works late, but never states this as a preference.
- A technical conclusion is still uncertain.
- The assistant infers a favored tool from a few recent choices.
- The new statement conflicts with an existing memory and replacement intent is unclear.

## Never auto-save

- One-day schedule exceptions.
- Temporary location, mood, or transient availability.
- Text supplied only for translation, proofreading, or rewriting.
- Random personal details with no future workflow value.
- Sensitive personal attributes, medical information, precise home location, political/religious identity, sexuality, criminal record, or other highly private details.
- Current progress, due dates, estimates, and task content already stored in the owning task.

Sensitive information may be saved only when the user explicitly asks. Store the minimum useful summary and mark `privacy: summary_only` where suitable.

## Forget semantics

“Forget” means removing or correcting the current authoritative record, not adding a second contradictory entry. Preserve only the minimum operation comment required for audit when the user has not asked to erase all trace; if the user asks for complete deletion, delete the memory and do not copy its content into a comment.
