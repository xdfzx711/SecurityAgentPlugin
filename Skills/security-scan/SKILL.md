---
name: security-scan
description: "Multi-agent security vulnerability scanning, verification, and PoC validation for codebases. Use when the user asks for a general security scan, vulnerability scan, security audit, 0-day research, exploitability review, PoC validation, or codebase vulnerability assessment across authentication, authorization, injection, cryptography, secrets, infrastructure, APIs, business logic, race conditions, or resource abuse."
---

# Security Scan

Run a multi-agent security audit pipeline for general codebase vulnerability assessment.

Use this skill for ordinary application, infrastructure, API, auth, crypto, injection, logic,
race-condition, and resource-abuse scanning.

For AI/ML third-party component interface-boundary analysis in GPU compute platforms, use the
`aiml-interface-boundary-scan` skill instead.

## Workflow

The default workflow has three phases:

1. Discovery: scan the target and produce candidate findings.
2. Verification: cross-check findings through independent review.
3. Validation: produce PoC code or a verification guide for confirmed issues.

Load only the relevant reference:

- Discovery: [references/phase1-discovery.md](references/phase1-discovery.md)
- Verification: [references/phase2-verification.md](references/phase2-verification.md)
- Validation: [references/phase3-validation.md](references/phase3-validation.md)
- Report templates: [references/report-templates.md](references/report-templates.md)
- General vulnerability taxonomy: [references/vulnerability-categories.md](references/vulnerability-categories.md)

## Pre-Flight

Check whether the target project has useful context files:

1. `{project_path}/CLAUDE.md`
2. `{project_path}/.claude-index/`

If both exist, instruct agents to read them before scanning. If either is missing, continue with
direct repository exploration unless the user explicitly asks to generate an index first.

Collect or infer:

- Target project path.
- Report output directory, defaulting to `{project}/security-report/`.
- Report language.
- Phase selection: discovery only, verification only, validation only, or full pipeline.

## General Security Audit Domains

Phase 1 agent domains:

- Authentication and authorization.
- Input validation and injection.
- Cryptography and secrets.
- Container and infrastructure.
- API and network security.
- Logic, state, race conditions, and resource abuse.

Use [references/vulnerability-categories.md](references/vulnerability-categories.md) for taxonomy and
[references/phase1-discovery.md](references/phase1-discovery.md) for detailed instructions.

## Expected Outputs

Phase 1:

```text
{report_dir}/phase1-discovery/detail-reports/{agent-name}-scan-report.md
{report_dir}/phase1-discovery/security-audit-final-report.md
```

Phase 2:

```text
{report_dir}/phase2-verification/detail-reports/round1/{agent-name}-verify-r1.md
{report_dir}/phase2-verification/detail-reports/round2/{agent-name}-verify-r2.md
{report_dir}/phase2-verification/verification-final-report.md
```

Phase 3:

```text
{report_dir}/phase3-validation/poc/{vuln-id}/
{report_dir}/phase3-validation/analysis/{vuln-id}/
{report_dir}/phase3-validation/validation-final-report.md
```

## Team Orchestration Pattern

For each phase:

1. Create a team with a descriptive name such as `security-scan-phase1`.
2. Create one task per scan domain or finding group.
3. Spawn agents with isolated worktrees when code changes or report writing may conflict.
4. Give each agent the target path, report path, language, and relevant reference.
5. Monitor progress and consolidate outputs after agents finish.
6. Shut down agents and clean up the team.

Agent prompt essentials:

```text
You are a senior security engineer.
Target project: {project_path}
Report directory: {report_dir}
Assignment: {specific task}

Read project context files first if present:
- {project_path}/CLAUDE.md
- {project_path}/.claude-index/

Read the relevant security-scan reference file before working.
Write your report to the assigned output path.
Every finding must include evidence, impact, confidence, and validation guidance.
```

## Report Quality Standards

- Cite concrete evidence: files, lines, routes, configs, HTTP behavior, schemas, or deployment metadata.
- Separate confirmed vulnerabilities from candidate vulnerabilities that still require manual validation.
- Include confidence, severity, and assumptions.
- Include safe manual validation steps.
- Avoid destructive testing unless explicitly authorized.
