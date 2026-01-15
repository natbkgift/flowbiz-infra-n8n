# CODEX Pre-flight Checklist (PR0 Governance)

**Purpose:** Mandatory gate before opening any PR.

1) Scope Check
- Confirm PR type (feat/fix/chore/docs/infra) and single Blueprint phase only.

2) Secret Check
- Run `git grep -i "secret\|token\|key="` and ensure no credentials.

3) Local Test
- Run `ruff check .`
- Run `pytest`

4) Contract Check
- If schemas changed, update `docs/PROJECT_CONTRACT.md` to match.
