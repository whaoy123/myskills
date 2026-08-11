# Optional Codex subagent templates

These files are optional role templates for `tiered-model-orchestrator`.
The skill itself does not require them.

Codex loads project-scoped custom agents from `.codex/agents/*.toml` and personal agents from `~/.codex/agents/*.toml`.
Copy only the roles you actually want to install.

Included roles:

- `explorer.toml` -> `orchestrator_explorer`: read-only investigation and evidence gathering.
- `worker.toml` -> `orchestrator_worker`: bounded implementation with explicit file ownership.
- `tester.toml` -> `orchestrator_tester`: independent validation and regression testing.
- `reviewer.toml` -> `orchestrator_reviewer`: read-only adversarial review.

All templates default to:

```toml
model = "gpt-5.6-luna"
model_reasoning_effort = "max"
```

The parent conversation remains the orchestrator. Installing these templates must not introduce a second controller layer.

If you prefer to use Codex built-in roles, `worker` and `explorer` are already available. The custom names above intentionally avoid overriding those built-ins.

You may also set project or personal defaults in the normal Codex config instead of pinning every custom agent:

```toml
[agents]
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "max"
# Leave max_concurrent_threads_per_session unset if Codex should choose the default.
```
