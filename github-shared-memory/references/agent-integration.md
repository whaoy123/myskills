# Agent instruction template

Configure the repository location once per machine, then add this concise instruction to the relevant project/global agent instructions:

```markdown
## Shared project memory

Use the `github-shared-memory` skill for long-running project work.
Memory repository: `<absolute local path or GitHub URL>`.
Before relevant work, read `PROFILE.md`, `CURRENT.md`, and the matching project files.
Record only confirmed durable facts and current handoff state. Review the diff before any commit; never push memory changes without current user authorization.
```

For a web client, connect the same private GitHub repository through its GitHub connector or MCP integration. The web client must follow the same read/update rules; its native product memory remains separate and non-authoritative.

## First repository setup

Create the repository manually or through an authorized agent action, then add this minimal starter set:

```markdown
<!-- PROFILE.md -->
# Profile

## Collaboration preferences

- Add only preferences that materially affect future work.
```

```markdown
<!-- CURRENT.md -->
# Current work

No active project recorded yet.
```

Do not place access tokens or copied private conversation histories in this repository. Make the repository private unless the user intentionally wants it shared.
