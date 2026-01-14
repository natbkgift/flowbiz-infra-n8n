# Guardrails

## Philosophy
Guardrails are **non-blocking** guidance mechanisms that surface violations through CI comments. The human developer remains in control and may override when appropriate.

## Principles

### 1. Non-Blocking by Design
- CI checks **do not** fail builds
- Violations are surfaced as warnings
- Human judgment is the final arbiter

### 2. Scope Protection
- Detect out-of-scope features
- Prevent architectural drift
- Maintain template purity

### 3. Developer Autonomy
- Developers can proceed despite warnings
- Context-aware overrides permitted
- Trust over enforcement

## Automated Checks

### Linting (Ruff)
```bash
ruff check .
```
**Status:** Non-blocking
**Purpose:** Code style consistency

### Testing (Pytest)
```bash
pytest -q
```
**Status:** Non-blocking
**Purpose:** Ensure functionality

### Scope Validation
**Patterns Flagged:**
- Authentication code
- Database models
- Billing logic
- Queue/worker systems
- Admin UI code

**Status:** Warning only
**Action:** Review and justify if necessary

## PR Requirements

### Mandatory Sections
- **Summary**: What and why
- **Testing**: How verified
- **Checklist**: Scope, docs, security

### Persona Labels
Tag PRs with affected areas:
- `persona:core` - Application logic
- `persona:infra` - Docker, Nginx, deployment
- `persona:docs` - Documentation updates

### Pre-flight Checklist
See `docs/CODEX_PREFLIGHT.md` for complete list.

## Scope Boundaries

### ✅ Acceptable Changes
- Bug fixes in existing endpoints
- Documentation improvements
- Performance optimizations
- Security patches
- Test improvements

### ⚠️ Needs Justification
- New dependencies
- Architecture changes
- Environment variable additions
- API contract modifications

### ❌ Scope Violations
- Business logic endpoints
- User authentication
- Database integrations
- External service calls (beyond health checks)
- Admin dashboards

## Override Protocol

If you must override a guardrail:

1. **Document Reason**: Explain in PR description
2. **Tag Appropriately**: Add `override:justified` label
3. **Seek Review**: Request maintainer approval
4. **Update Docs**: Reflect changes in documentation

## Example Workflow

### Green Path
```bash
# Make changes
git checkout -b feature/improve-logging

# Run checks locally
ruff check .
pytest -q

# All pass → Create PR
gh pr create
```

### Warning Path
```bash
# Make changes
git checkout -b feature/add-caching

# Run checks
ruff check .  # ⚠️ Warning: new dependency detected
pytest -q     # ✅ Pass

# Review warning
# Add justification to PR description
# Create PR with explanation
gh pr create
```

### Override Path
```bash
# Make changes that violate scope
git checkout -b hotfix/critical-security

# Check flags violation
# Document in PR:
# - Why override necessary
# - Security impact
# - Alternative considered

gh pr create --label "override:justified"
```

## Maintenance

### Updating Guardrails
1. Propose changes in issue
2. Discuss with maintainers
3. Update CI workflows
4. Document in this file

### False Positives
If guardrails trigger incorrectly:
1. Report in issue
2. Provide context
3. Suggest pattern refinement

## Questions?
Guardrails unclear? Raise an issue or check `docs/CODEX_PREFLIGHT.md` for detailed requirements.
