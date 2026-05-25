---
name: security-scan
description: "Multi-agent security vulnerability scanning, verification, and PoC validation for codebases and AI/ML platform integrations. Use when the user asks for a security scan, vulnerability scan, security audit, 0-day research, PoC validation, AI/ML platform security review, GPU platform security review, interface enumeration, boundary modeling, suspicious pattern reporting, or analysis of third-party ML components such as MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus/DCGM, MinIO, dashboards, runtimes, artifact stores, telemetry endpoints, streaming connectors, or management APIs."
---

# Security Scan

Run a multi-agent security audit pipeline. The default workflow has three phases:

1. Discovery: scan the target and produce candidate findings.
2. Verification: cross-check findings through independent review.
3. Validation: produce PoC code or a verification guide for confirmed issues.

For detailed phase instructions, load only the relevant reference:

- Discovery: [references/phase1-discovery.md](references/phase1-discovery.md)
- Verification: [references/phase2-verification.md](references/phase2-verification.md)
- Validation: [references/phase3-validation.md](references/phase3-validation.md)
- Report templates: [references/report-templates.md](references/report-templates.md)
- General vulnerability taxonomy: [references/vulnerability-categories.md](references/vulnerability-categories.md)
- AI/ML interface boundary profile: [references/ai-ml-interface-boundary-scan.md](references/ai-ml-interface-boundary-scan.md)

## Profile Selection

Before scanning, determine whether the task is a general code security audit or an AI/ML interface
boundary audit.

Use the general profile when the user asks for ordinary application, infrastructure, API, auth,
crypto, injection, or logic vulnerability scanning.

Use the AI/ML Interface Boundary Profile when the target is an AI/ML platform, GPU compute
platform, notebook platform, MLOps stack, model-serving platform, or a product integrating
third-party AI/ML components. This includes MLflow, Ray, Jupyter, jupyter-server-proxy, Dask,
Open WebUI, Kubeflow, Triton, Prometheus/DCGM, MinIO, object stores, runtime proxies, dashboards,
job APIs, artifact registries, telemetry services, external model connectors, SSE streams, tool
or function execution surfaces, and management APIs.

When using the AI/ML profile, load
[references/ai-ml-interface-boundary-scan.md](references/ai-ml-interface-boundary-scan.md) and
produce interface and boundary artifacts before making vulnerability claims.

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
- Scan profile: general security audit or AI/ML interface boundary audit.

## General Security Audit Workflow

Use this workflow for ordinary vulnerability scanning.

Phase 1 agent domains:

- Authentication and authorization.
- Input validation and injection.
- Cryptography and secrets.
- Container and infrastructure.
- API and network security.
- Logic, state, race conditions, and resource abuse.

Use [references/vulnerability-categories.md](references/vulnerability-categories.md) for taxonomy and
[references/phase1-discovery.md](references/phase1-discovery.md) for detailed instructions.

Phase 1 output:

```text
{report_dir}/phase1-discovery/detail-reports/{agent-name}-scan-report.md
{report_dir}/phase1-discovery/security-audit-final-report.md
```

Phase 2 output:

```text
{report_dir}/phase2-verification/detail-reports/round1/{agent-name}-verify-r1.md
{report_dir}/phase2-verification/detail-reports/round2/{agent-name}-verify-r2.md
{report_dir}/phase2-verification/verification-final-report.md
```

Phase 3 output:

```text
{report_dir}/phase3-validation/poc/{vuln-id}/
{report_dir}/phase3-validation/analysis/{vuln-id}/
{report_dir}/phase3-validation/validation-final-report.md
```

## AI/ML Interface Boundary Workflow

Use this workflow when the user's goal is to scan AI/ML platform integration risks or third-party
component interface exposure. The goal is to answer:

```text
Which interfaces are exposed, who should be able to access them, who may actually reach them,
and what security boundary mismatch does that imply?
```

Phase 1 must run the four-module pipeline from
[references/ai-ml-interface-boundary-scan.md](references/ai-ml-interface-boundary-scan.md):

1. Component Fingerprinter.
2. Interface Enumerator.
3. Boundary Analyzer.
4. Suspicious Pattern Reporter.

Recommended Phase 1 agent roles:

- Component fingerprinter: identify AI/ML components, versions, entrypoints, and deployment context.
- Interface enumerator: enumerate API, Dashboard, Runtime, Artifact, Telemetry, Management,
  Streaming, Auth/Admin, Model Serving, and Storage interfaces.
- Boundary analyzer: compare expected authentication, authorization, exposure, and trust boundaries
  with observed deployment and route behavior.
- Suspicious pattern reporter: produce reviewable findings with evidence, possible impact, manual
  validation, and safe testing notes.
- Component specialists as needed: MLflow, Ray, Jupyter/jupyter-server-proxy, Dask, Open WebUI,
  Kubeflow, Triton, Prometheus/DCGM, MinIO/S3, or other detected components.

Primary Phase 1 outputs:

```text
{report_dir}/phase1-discovery/interface-enumeration-table.yaml
{report_dir}/phase1-discovery/boundary-model-table.yaml
{report_dir}/phase1-discovery/suspicious-pattern-report.md
{report_dir}/phase1-discovery/detail-reports/{agent-name}-scan-report.md
```

The suspicious pattern taxonomy in the AI/ML profile is deliberately open-ended. Treat P1-P6 as
seed patterns only:

- Mixed Routing Authentication Coverage Gap.
- Unsafe Default / Trusted-Internal Assumption.
- Artifact / Registry Semantic Reuse Mismatch.
- Runtime Proxy / WebSocket Auth Inconsistency.
- Dashboard Management Endpoint Exposure.
- External AI Backend Trust Confusion.

Agents must also identify and name new pattern families when evidence shows a boundary mismatch
outside those seeds. Examples include telemetry cross-tenant disclosure, model-serving control-plane
exposure, gateway path normalization mismatch, confused identity propagation, route-method policy
gaps, storage boundary drift, or external tool execution trust gaps.

Do not overstate suspicious patterns as confirmed vulnerabilities. Use language such as suspected,
possible, likely, or requires manual validation unless exploitability is proven.

## Verification And Validation

For general findings, use the standard Phase 2 and Phase 3 references.

For AI/ML interface-boundary findings, verification should answer:

- Is the interface actually reachable in the platform deployment?
- Is authentication enforced for every route stack, protocol, and HTTP method?
- Is authorization scoped to user, workspace, project, namespace, tenant, or admin role?
- Does the interface change state or expose sensitive data?
- Does the component rely on a trusted-network assumption that the platform violates?
- Does external input, external backend output, artifact metadata, telemetry, or proxy routing cross
  a trust boundary?

Validation must remain non-destructive unless the user explicitly authorizes a controlled test
environment. Prefer static analysis, route metadata, OpenAPI, frontend route extraction, safe GET,
HEAD, and OPTIONS probes. Do not submit jobs, execute code, delete resources, shut down services,
restart components, load or unload models, mutate registries, or read real user artifacts during
automated discovery.

## Team Orchestration Pattern

For each phase:

1. Create a team with a descriptive name such as `security-scan-phase1`.
2. Create one task per scan domain, module, component, or finding group.
3. Spawn agents with isolated worktrees when code changes or report writing may conflict.
4. Give each agent the target path, report path, selected profile, language, and relevant reference.
5. Monitor progress and consolidate outputs after agents finish.
6. Shut down agents and clean up the team.

Agent prompt essentials:

```text
You are a senior security engineer.
Target project: {project_path}
Report directory: {report_dir}
Selected profile: {general | ai-ml-interface-boundary}
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
- Separate confirmed vulnerabilities from suspicious boundary mismatches.
- Include confidence, severity, and assumptions.
- Include safe manual validation steps.
- Avoid destructive testing unless explicitly authorized.
- For AI/ML interface reports, always include expected boundary vs observed boundary.
