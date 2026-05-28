---
name: aiml-interface-boundary-scan
description: "Scan AI/ML third-party components after integration into GPU compute platforms, focusing on platform interface-layer security risks, exposed component interfaces, trust-boundary mismatches, authentication and authorization coverage gaps, dashboard/runtime/artifact/telemetry/model-serving/management surfaces, and candidate vulnerability reporting. Use for AI/ML platform security review, GPU platform interface boundary modeling, MLOps component exposure analysis, or third-party ML components such as MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus/DCGM, MinIO, object stores, notebook proxies, runtime proxies, SSE streams, external model connectors, and management APIs."
---

# AI/ML Interface Boundary Scan

Use this skill to scan platform-interface security risks introduced when third-party AI/ML
components are integrated into a GPU compute platform.

The goal is not generic vulnerability hunting. The goal is to answer:

```text
Which AI/ML component interfaces are exposed, who should be able to access them, who may actually
reach them after platform integration, and what security boundary mismatch does that imply?
```

## Primary Reference

Always load [references/ai-ml-interface-boundary-scan.md](references/ai-ml-interface-boundary-scan.md)
as the primary workflow.

Use [references/aiml-risk-taxonomy.md](references/aiml-risk-taxonomy.md) as the risk taxonomy for
candidate generation, scoring, verification planning, and report terminology. Treat it as a seed
taxonomy, not an exhaustive list.

Use [references/aiml-report-template.md](references/aiml-report-template.md) for Phase 1 reports,
Phase 2 manual verification plans, structured YAML appendices, and research pattern summaries.

Use general security knowledge only as supporting reasoning. Do not replace the interface-boundary
workflow with a generic scan for XSS, SQL injection, cryptography, dependency, or race-condition
issues unless those issues arise from an AI/ML platform interface boundary mismatch.

## Default AI/ML Interface Boundary Workflow

Use this workflow as the default process instead of the general security-scan
`Discovery -> Verification -> Validation` model:

```text
Component Fingerprinting
  -> Interface Enumeration
  -> Boundary Modeling
  -> Candidate Vulnerability Generation
  -> Manual Verification Planning
  -> Safe Validation Guidance
```

1. Component Fingerprinting: identify AI/ML components, versions, entrypoints, deployment mode, and
   platform exposure path.
2. Interface Enumeration: enumerate API, dashboard, runtime proxy, artifact, telemetry, streaming,
   model serving, storage, auth/admin, and management interfaces.
3. Boundary Modeling: compare expected authentication, authorization, exposure, trust, tenant,
   workspace, namespace, object, runtime, artifact, and management boundaries with observed
   deployment and route behavior.
4. Candidate Vulnerability Generation: convert boundary mismatches into concrete candidate
   vulnerabilities with severity, score, confidence, evidence, impact, false-positive conditions,
   and remediation guidance.
5. Manual Verification Planning: turn candidates into a concrete non-destructive manual verification
   plan when the user asks for verification or a full pipeline.
6. Safe Validation Guidance: provide safe validation guidance and explicit unsafe-test boundaries.
   Do not default to PoC exploitation or destructive validation.

## Agent Work Mode

Use a pipeline with focused parallel branches, not generic vulnerability-category agents.

Primary pipeline:

```text
component-fingerprint
  -> interface-enumerator
  -> boundary-analyzer
  -> candidate-vulnerability-generator
  -> manual-verification-planner
```

After `interface-enumerator` produces an interface inventory, run focused interface-family agents in
parallel when the target contains relevant surfaces:

```text
interface-enumerator
  -> artifact-registry
  -> runtime-management
  -> dashboard-proxy
  -> telemetry-logging
  -> deployment-config
  -> cross-tenant-authz
```

The `boundary-analyzer` must consume the component inventory, interface inventory, and focused
agent outputs before candidate vulnerabilities are generated.

## Agent Roles

Use interface-boundary roles instead of generic Phase 1 domains such as injection, cryptography,
secrets, or race conditions. Only analyze those generic vulnerability classes when they are directly
caused by an AI/ML platform interface-boundary mismatch.

Recommended roles:

| Agent | Focus |
| --- | --- |
| component-fingerprint | Identify AI/ML components such as MLflow, Ray, Triton, Jupyter, Kubeflow, Prometheus/DCGM, MinIO, object stores, notebook proxies, model-serving services, and deployment entrypoints. |
| interface-enumerator | Enumerate API, dashboard, runtime, artifact, telemetry, management, model-serving, storage, streaming, and auth/admin interfaces. |
| boundary-analyzer | Compare platform boundaries and component boundaries; identify authentication, authorization, exposure, tenant, workspace, namespace, object, and trust mismatches. |
| artifact-registry | Inspect model, checkpoint, dataset, prompt, artifact URI, object-store, local-path, bucket, and registry boundary behavior. |
| runtime-management | Inspect job submit/cancel/logs, kernels, notebooks, terminals, model load/unload, runtime proxy, and execution-control interfaces. |
| dashboard-proxy | Inspect dashboard proxying, path rewrite, WebSocket/SSE upgrades, host/path controllability, backend routing, and proxy auth consistency. |
| telemetry-logging | Inspect metrics, traces, logs, GPU/node/job/pod/queue visibility, and cross-tenant operational data exposure. |
| deployment-config | Inspect Helm, Kubernetes Service, Ingress, NodePort, gateway, service mesh, default auth, environment variables, and exposure configuration. |
| cross-tenant-authz | Inspect user/project/workspace/namespace/object authorization consistency across API, storage, runtime, telemetry, and model-serving interfaces. |
| candidate-vulnerability-generator | Convert boundary mismatches into concrete candidate vulnerabilities with evidence, severity, score, confidence, false-positive conditions, and validation preview. |
| manual-verification-planner | Convert candidates into a safe manual verification plan with evidence gaps, read-only checks, forbidden actions, expected signals, and decision placeholders. |

Each agent output must include detected interfaces or configs, expected boundary, observed boundary,
boundary mismatch hypothesis, supporting evidence, evidence gaps, safe validation preview, and
candidate IDs supported by the role when applicable.

## Expected Outputs

Phase 1 primary report:

```text
{report_dir}/phase1-discovery/ai-ml-candidate-vulnerability-report.md
```

Phase 2 manual verification plan:

```text
{report_dir}/phase2-verification/ai-ml-manual-verification-plan.md
```

Optional raw artifacts:

```text
{report_dir}/phase1-discovery/raw/interface-enumeration-table.yaml
{report_dir}/phase1-discovery/raw/boundary-model-table.yaml
{report_dir}/phase1-discovery/raw/candidate-vulnerabilities.yaml
```

Do not make raw YAML or per-agent detail reports the primary user-facing output. The main report
should be Chinese by default unless the user requests another language.

## Safety Rules

- Do not submit jobs, execute code, delete resources, shut down services, restart components, load
  or unload models, mutate registries, or read real user artifacts during automated discovery.
- Prefer source review, route metadata, OpenAPI, frontend route extraction, Kubernetes or Helm
  configuration, and safe GET, HEAD, and OPTIONS probes.
- For auth testing, prefer read-only endpoints and document exact request/response behavior.
- For WebSocket or SSE, record handshake and routing behavior; do not send payloads that trigger
  runtime execution.
- Mark dangerous endpoints as `destructive-do-not-call`.

## Phase 2 Prompting Rule

When using Phase 2, prompt the verifier as a boundary auditor, not as an exploit developer.

The prompt must include:

- The Phase 1 candidate report path.
- The exact candidate IDs to verify.
- The target project or deployment evidence path.
- The interface type, expected boundary, observed boundary, evidence gaps, and false-positive
  conditions for each candidate.
- A prohibition on destructive testing.
- A required output path: `{report_dir}/phase2-verification/ai-ml-manual-verification-plan.md`.

Use the Phase 2 prompt template in
[references/ai-ml-interface-boundary-scan.md](references/ai-ml-interface-boundary-scan.md).

## Report Quality Standards

- Every candidate must include expected boundary vs observed boundary.
- Every candidate must include evidence, missing evidence, confidence, severity, numeric score, and
  safe manual validation steps.
- Do not overstate candidates as confirmed vulnerabilities.
- Use status values such as `candidate_requires_manual_validation`,
  `confirmed_by_non_destructive_probe`, `needs_more_evidence`, or `not_a_vulnerability_contextual`.
- Final user-facing output must be concrete candidate vulnerabilities, not pattern-only findings.
