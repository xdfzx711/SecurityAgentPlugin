# AI/ML Interface Boundary Scan

Use this reference when the target is an AI/ML platform, GPU compute platform, model-serving
platform, notebook platform, MLOps stack, or a product that integrates third-party AI/ML components
such as MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus, DCGM, MinIO, or
similar services.

The purpose is to enumerate exposed interfaces, model their expected security boundaries, identify
boundary mismatches, and produce concrete candidate vulnerabilities with severity, score, evidence,
and safe manual validation guidance.

For risk categories, load [aiml-risk-taxonomy.md](aiml-risk-taxonomy.md). Use it as a seed taxonomy,
not an exhaustive list. If evidence supports a new AI/ML platform interface-boundary risk category,
define a proposed category in the report appendix.

For report structure, load [aiml-report-template.md](aiml-report-template.md). Use it for the
primary Chinese Phase 1 report, Phase 2 manual verification plan, structured YAML appendix, and
research pattern summary.

## Core Question

When a third-party AI/ML component is integrated into a GPU/AI platform, do its API, dashboard,
runtime, artifact, telemetry, streaming, model-serving, storage, or management interfaces inherit a
security role they were not designed for?

Look for mismatches between:

- The component's original deployment assumptions.
- The platform's actual exposure model.
- The authentication and authorization applied by the platform.
- The trust placed in external inputs, external backends, proxy targets, artifact metadata,
  telemetry data, runtime channels, or route headers.

## Phase 1 Pipeline

Run these modules in order:

```text
Component Fingerprinter
  -> Interface Enumerator
  -> Boundary Analyzer
  -> Candidate Vulnerability Generator
  -> Manual Verification Preview
```

## Agent Work Mode And Roles

Use a pipeline with focused parallel branches.

Primary dependency chain:

```text
component-fingerprint
  -> interface-enumerator
  -> boundary-analyzer
  -> candidate-vulnerability-generator
  -> manual-verification-planner
```

Focused interface-family agents may run in parallel after `interface-enumerator` creates the initial
interface inventory:

```text
interface-enumerator
  -> artifact-registry
  -> runtime-management
  -> dashboard-proxy
  -> telemetry-logging
  -> deployment-config
  -> cross-tenant-authz
```

Do not use generic Phase 1 agent domains such as input validation, cryptography, secrets, container
security, or race conditions unless the issue is directly tied to an AI/ML platform interface
boundary mismatch.

### Role Responsibilities

| Agent | Responsibility |
| --- | --- |
| component-fingerprint | Identify AI/ML third-party components, versions, images, packages, services, ports, routes, UI assets, and deployment entrypoints. Detect MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus/DCGM, MinIO/S3, notebook proxies, runtime proxies, model-serving services, artifact stores, and external model connectors. |
| interface-enumerator | Build the interface inventory from the component list. Record route, method, protocol, interface type, operation semantics, state-changing behavior, sensitive output, discovery source, observed exposure, and preliminary auth observation. |
| artifact-registry | Inspect models, checkpoints, datasets, prompts, artifact URIs, object-store paths, local paths, file URIs, buckets, registry metadata, and storage roots. Look for workspace, project, tenant, object, and storage-boundary drift. |
| runtime-management | Inspect job submit/cancel/logs, notebook kernels, terminals, runtime proxies, Ray Jobs, Jupyter sessions, model load/unload, inference management, and execution-control interfaces. Identify code-execution, workload-control, and runtime-scope risks. |
| dashboard-proxy | Inspect dashboard routes, reverse proxies, path rewrites, host/path controllability, WebSocket/SSE upgrades, backend direct access, route stack differences, and proxy authentication consistency. |
| telemetry-logging | Inspect metrics, traces, logs, Prometheus/DCGM endpoints, GPU/node/pod/job/queue visibility, scheduler metadata, model names, prompt or request metadata, and cross-tenant operational data exposure. |
| deployment-config | Inspect Helm values, Kubernetes Service, Ingress, Gateway, NodePort, service mesh, NetworkPolicy, environment variables, default auth settings, basic-auth/token config, and public/tenant/internal exposure paths. |
| cross-tenant-authz | Inspect user, project, workspace, namespace, tenant, object, owner-session, and admin authorization consistency across API, storage, runtime, telemetry, model-serving, and dashboard interfaces. |
| boundary-analyzer | Consume component, interface, deployment, and focused-agent outputs. For each interface, compare expected boundary vs observed boundary across authn, authz, exposure, trust, tenant scope, runtime scope, artifact scope, management control, and telemetry scope. |
| candidate-vulnerability-generator | Convert boundary mismatches into concrete candidate vulnerabilities. Assign class, CWE where applicable, severity, score, confidence, status, evidence, impact, attack preconditions, false-positive conditions, safe validation preview, and remediation guidance. |
| manual-verification-planner | Convert candidates into non-destructive manual verification plans. Define evidence gaps, required environment, read-only checks, logs/configs/responses to collect, forbidden dangerous actions, expected signals, and final decision placeholders. |

### Standard Agent Output

Every Phase 1 agent report should include:

```yaml
agent: <role name>
scope: <assigned component/interface/config family>
inputs_consumed:
  - <component inventory | interface inventory | deployment configs | previous reports>
detected_items:
  - <interfaces, configs, routes, components, or policy records>
expected_boundary:
  authentication: <required | optional | absent | unknown>
  authorization: <user | workspace | namespace | object | admin | absent | unknown>
  exposure: <internal-only | tenant-facing | public | admin-only | unknown>
  trust: <trusted-internal | untrusted-external | mixed | unknown>
observed_boundary:
  authentication: <evidence-backed observation>
  authorization: <evidence-backed observation>
  exposure: <evidence-backed observation>
  trust: <evidence-backed observation>
boundary_mismatch_hypotheses:
  - <specific mismatch hypothesis>
supporting_evidence:
  - <file, route, config, HTTP behavior, schema, policy, or deployment evidence>
evidence_gaps:
  - <what must be checked manually>
safe_validation_preview:
  - <read-only or config-review step>
candidate_ids_supported:
  - <candidate ID if already assigned, otherwise empty>
```

The `boundary-analyzer` must merge role outputs before `candidate-vulnerability-generator` writes
candidate records. The candidate generator must not invent candidates that are unsupported by the
component inventory, interface inventory, or boundary evidence.

### High-Effect Phase 1 Prompt Template

Use this prompt when assigning Phase 1. It works best because it defines the research object before
any scanning begins: third-party AI/ML components integrated into a GPU compute platform, their
exposed interfaces, and the platform boundary mismatches those interfaces create.

```text
You are a senior AI/ML platform security auditor. Your task is Phase 1 discovery for an
AI/ML interface-boundary scan.

Do not perform a generic web/app/code vulnerability scan. Do not start from XSS, SQL injection,
crypto, dependency, or ordinary business-logic categories. Only report those issues if they arise
from an AI/ML component interface boundary mismatch.

Research object:
Third-party AI/ML components integrated into a GPU compute platform, and the security risks created
at the platform interface layer after integration.

Core question:
Which AI/ML component interfaces are exposed, who should be able to access them, who may actually
reach them after platform integration, and what security boundary mismatch does that imply?

Target project or deployment evidence:
{project_path_or_evidence_path}

Report directory:
{report_dir}

Output:
{report_dir}/phase1-discovery/ai-ml-candidate-vulnerability-report.md

Language:
Chinese by default unless the user requests otherwise.

Run these four modules in order:

1. Component Fingerprinter
   - Identify AI/ML components, versions, entrypoints, deployment mode, and platform exposure path.
   - Look for MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus/DCGM, MinIO/S3,
     notebook proxies, runtime proxies, model-serving endpoints, artifact stores, telemetry, external
     model connectors, and management APIs.

2. Interface Enumerator
   - Enumerate exposed API, Dashboard, Runtime Proxy, Artifact/Registry, Telemetry, Streaming,
     Auth/Admin, Model Serving, Storage, and Management interfaces.
   - For each interface record route, method/protocol, operation semantics, state-changing behavior,
     sensitive output, observed exposure, auth observation, and discovery source.
   - Prefer source review, OpenAPI, frontend route extraction, deployment config, ingress/gateway
     policy, HEAD, OPTIONS, and safe GET.
   - Do not call submit, cancel, delete, restart, shutdown, load, unload, execute, mutate, upload, or
     registry-changing endpoints.

3. Boundary Analyzer
   - For each interface compare expected boundary vs observed boundary.
   - Evaluate authentication, authorization, exposure, trust, runtime scope, artifact scope,
     management control, telemetry scope, storage boundary, and external connector trust.
   - Identify whether the component assumes trusted-internal use while the platform exposes it to
     users, tenants, public routes, notebooks, gateways, proxies, or external backends.

4. Candidate Vulnerability Generator
   - Convert boundary mismatches into concrete candidate vulnerabilities.
   - Do not output only abstract patterns. Every candidate must name the affected component,
     interface, taxonomy risk category, boundary mismatch, vulnerability class, evidence, impact,
     confidence, severity, score, validation preview, false-positive conditions, and remediation
     guidance.
   - Use `aiml-risk-taxonomy.md` to assign A1-A8 when a candidate fits. If a candidate does not fit,
     propose a new risk category in the report appendix instead of forcing it into the closest class.
   - Use status values:
     candidate_requires_manual_validation, confirmed_by_non_destructive_probe, needs_more_evidence,
     or not_a_vulnerability_contextual.

Use the Agent Work Mode And Roles section when splitting work across agents. The component inventory
must feed the interface inventory; the interface inventory and focused interface-family reports must
feed boundary analysis; boundary analysis must feed candidate vulnerability generation.

Use [aiml-risk-taxonomy.md](aiml-risk-taxonomy.md) for risk categories and terminology. The taxonomy
contains seed categories, not a closed list. Internal heuristics to consider, but not use as final
titles:
- Mixed Routing Authentication Coverage Gap.
- Unsafe Default / Trusted-Internal Assumption.
- Artifact / Registry Semantic Reuse Mismatch.
- Runtime Proxy / WebSocket Auth Inconsistency.
- Dashboard Management Endpoint Exposure.
- External AI Backend Trust Confusion.
- Cross-tenant telemetry disclosure.
- Model-serving control-plane exposure.
- Gateway path normalization mismatch.
- Confused identity propagation.
- Route-method policy gap.
- Storage boundary drift.
- External tool execution trust gap.

Final report structure:
1. 执行摘要
2. 候选漏洞总览
3. 组件与接口枚举摘要
4. 边界分析摘要
5. 候选漏洞详情
6. Phase 2 人工验证预览
7. 附录：结构化结果摘要

Quality bar:
- Cite concrete files, routes, configs, policies, HTTP behavior, schemas, or deployment evidence.
- Distinguish observed evidence from inference.
- Do not call candidates confirmed unless the evidence proves the boundary failure.
- Include safe manual validation guidance for every candidate.
- If evidence is weak, keep the candidate as needs_more_evidence and state exactly what is missing.
```

### Compact Phase 1 Prompt

Use this shorter prompt when context is tight:

```text
Use $aiml-interface-boundary-scan Phase 1.

Target:
{project_path_or_evidence_path}

Write:
{report_dir}/phase1-discovery/ai-ml-candidate-vulnerability-report.md

Do not run a generic vulnerability scan. Scan AI/ML third-party components integrated into a GPU
compute platform. Identify components, enumerate exposed interfaces, model expected vs observed
security boundaries, and generate concrete candidate vulnerabilities from boundary mismatches.

For every candidate include component, interface, expected boundary, observed boundary, evidence,
taxonomy risk category, vulnerability class, CWE when applicable, severity, score, confidence,
status, impact, validation preview, false-positive conditions, and remediation guidance. Use A1-A8
when the candidate fits; propose a new category when evidence supports a boundary risk outside A1-A8.
Write the report in Chinese.

Use only passive or non-destructive discovery. Do not submit jobs, execute code, mutate registries,
delete resources, restart services, load/unload models, or read real user artifacts.
```

### Module 1: Component Fingerprinter

Identify deployed AI/ML components, versions, entrypoints, and deployment context.

Inputs:

- Base URL, host, port, Kubernetes service, ingress, Docker Compose service, Helm values.
- HTTP responses, static assets, OpenAPI docs, version endpoints.
- Source code route definitions, frontend route definitions, package manifests, deployment files.

High-value component signals:

| Component | Signals |
| --- | --- |
| MLflow | `/api/2.0/mlflow/*`, experiment/run/model registry routes, MLflow UI assets |
| Ray | dashboard UI, Jobs API, Serve routes, `/api/jobs`, `/api/serve` |
| Jupyter | `/api/kernels`, `/api/sessions`, `/terminals`, `/proxy/`, notebook static assets |
| Dask | Dask dashboard title, scheduler/worker pages, `/proxy/<port>/<host>/...` |
| Open WebUI | Open WebUI UI, external connections, OpenAI-compatible settings, SSE chat stream |
| Kubeflow | central dashboard, Pipelines API, profile/namespace routes |
| Triton | inference API, model repository, model metadata endpoint |
| Prometheus/DCGM | `/metrics`, Prometheus API/UI, DCGM metric names |
| MinIO/S3 | artifact bucket endpoints, console UI, S3-compatible API |

### Module 2: Interface Enumerator

Enumerate exposed interfaces and label protocol, operation semantics, and preliminary boundary.

Interface types:

- Job Control Interface: submit, read, search, cancel, stop, delete, logs.
- Artifact / Registry Interface: model, checkpoint, prompt, dataset, artifact URI, object store.
- Runtime Proxy Interface: notebook, terminal, kernel, code-server, VNC, RStudio, WebSocket proxy.
- Dashboard Management Interface: dashboard state, management actions, worker proxy.
- Telemetry Interface: GPU, node, pod, namespace, job, queue, scheduler metrics.
- Streaming / External Connector Interface: SSE, external model backend, tool/function call stream.
- Auth / Admin Interface: login, users, roles, permissions, default admin, bootstrap config.
- Model Serving Interface: inference, model metadata, model repository, load/unload, ensemble routes.
- Storage / Secret Interface: buckets, mounted volumes, credentials, connection settings.

Prefer passive and non-destructive sources:

1. OpenAPI, docs, route metadata, frontend static route extraction.
2. Kubernetes ingress/service and Helm value inspection.
3. HEAD, OPTIONS, and safe GET probes.
4. Known route dictionaries for identified components.

Do not trigger destructive or workload-changing operations during discovery. Identify but do not call
DELETE, shutdown, submit, cancel, restart, terminate, model-load, model-unload, registry mutation, or
arbitrary-code paths.

### Module 3: Boundary Analyzer

For each interface, compare expected boundary against observed behavior and deployment context.

Boundary dimensions:

- Authentication: Is caller identity verified on every route stack and protocol?
- Authorization: Is the caller allowed to operate on this user, project, workspace, namespace, tenant,
  object, or admin function?
- Exposure: Is an internal-only or admin-only interface reachable through ingress, gateway, proxy, or
  tenant network?
- Trust: Are external inputs, external services, artifact metadata, dashboard parameters, route
  headers, or stream events treated as trusted?
- Runtime: Are notebooks, terminals, kernels, WebSockets, VNC, and code-server scoped to the owning
  user or session?
- Artifact: Are model, checkpoint, prompt, dataset, and artifact roots bound to the correct workspace
  and storage backend?
- Management: Are delete, shutdown, cancel, restart, load, unload, and scale operations protected?
- Telemetry: Are metrics scoped so tenants cannot read other users' jobs, pods, nodes, GPUs, prompts,
  queues, or resource usage?
- External Connector: Are OpenAI-compatible endpoints, tools, function calls, and SSE events treated
  as untrusted data?

### Module 4: Candidate Vulnerability Generator

Convert boundary mismatches into concrete candidate vulnerabilities. Final output must describe
specific possible vulnerabilities, not only abstract mismatch categories.

Good candidate vulnerability titles:

- Potential unauthenticated access to MLflow job-control endpoints.
- Potential default-admin takeover of MLflow basic-auth deployment.
- Potential local artifact file exposure through MLflow registry source metadata.
- Potential unauthenticated DELETE access to Ray Dashboard management endpoints.
- Potential WebSocket authentication bypass in proxied Jupyter runtime backend.
- Potential reflected XSS in Dask dashboard proxy route.
- Potential unauthenticated Ray Jobs API code execution exposure.
- Potential script execution from untrusted OpenAI-compatible SSE backend in Open WebUI.
- Potential cross-tenant GPU/job telemetry disclosure through metrics endpoint.
- Potential model repository load/unload control-plane exposure.

Candidate vulnerability record:

```yaml
vulnerability_id: CAND-AIML-001
title: Potential unauthenticated access to MLflow job-control endpoints
component: MLflow
component_version: 3.x | unknown
affected_interface:
  endpoint_or_route: /ajax-api/3.0/jobs/*
  method_or_protocol: GET/POST
  interface_type: Job Control
vulnerability_class: Missing Authentication / Broken Access Control
cwe:
  - CWE-306
  - CWE-862
severity: high
score: 8.1
confidence: high
status: candidate_requires_manual_validation
detection_basis:
  - mixed_routing_authentication_coverage_gap
evidence:
  - FastAPI job route discovered.
  - Route performs job-control operation.
  - Basic-auth deployment suspected.
boundary_mismatch:
  expected: Job-control endpoints require authenticated and authorized users.
  observed: FastAPI job routes may not share the primary basic-auth route chain.
attack_preconditions:
  - Attacker can reach the MLflow service or platform route.
possible_impact:
  - Unauthenticated job submit, read, search, or cancel may be possible.
validation_steps:
  - Check whether auth middleware covers the FastAPI job router.
  - Test unauthenticated access only with non-destructive read/search endpoints.
  - Confirm gateway policy covers the route prefix and all methods.
safe_testing_note: Do not submit or cancel jobs during automated discovery.
false_positive_conditions:
  - Gateway authentication protects the route before traffic reaches MLflow.
  - Job execution is disabled and all job endpoints return authenticated errors.
```

Use candidate status values:

- `candidate_requires_manual_validation`: evidence supports a vulnerability hypothesis, but
  exploitability has not been confirmed.
- `confirmed_by_non_destructive_probe`: a safe probe confirmed the relevant boundary failure.
- `needs_more_evidence`: interface exists, but exposure or auth behavior is too uncertain.
- `not_a_vulnerability_contextual`: the interface is expected and protected in this deployment.

## Internal Boundary-Mismatch Heuristics

Use [aiml-risk-taxonomy.md](aiml-risk-taxonomy.md) for candidate risk categories. Use the heuristics
below as internal detection bases, not final report titles:

| ID | Internal Heuristic | Typical Candidate Vulnerability Classes | Typical CWE |
| --- | --- | --- | --- |
| P1 | Mixed Routing Authentication Coverage Gap | Missing Authentication, Authentication Bypass, Broken Access Control | CWE-306, CWE-287, CWE-862 |
| P2 | Unsafe Default / Trusted-Internal Assumption | Use of Default Credentials, Missing Authentication, Exposed Dangerous API | CWE-1392, CWE-798, CWE-306 |
| P3 | Artifact / Registry Semantic Reuse Mismatch | Path Traversal, Improper Authorization, Trust Boundary Violation | CWE-22, CWE-73, CWE-862, CWE-501 |
| P4 | Runtime Proxy / WebSocket Auth Inconsistency | WebSocket Authentication Bypass, Improper Access Control | CWE-306, CWE-287, CWE-862 |
| P5 | Dashboard Management Endpoint Exposure | Missing Authorization for Management Action, Improper Access Control | CWE-862, CWE-284, CWE-352 |
| P6 | External AI Backend Trust Confusion | XSS, Confused Deputy, Untrusted Tool Invocation | CWE-79, CWE-116, CWE-441, CWE-94 |

Also consider:

- Cross-tenant telemetry disclosure.
- Model-serving control-plane exposure.
- Artifact storage boundary drift.
- Gateway path normalization mismatch.
- Admin bootstrap or first-run exposure.
- Capability amplification through notebook context.
- Confused identity propagation.
- Route-method policy gap.
- External tool execution trust gap.
- Version-specific security assumption drift.

## Scoring

Assign each candidate a severity and numeric score. Scores are prioritization aids, not final CVSS
unless the evidence is strong enough to calculate CVSS directly.

Severity bands:

| Severity | Score |
| --- | --- |
| Critical | 9.0-10.0 |
| High | 7.0-8.9 |
| Medium | 4.0-6.9 |
| Low | 0.1-3.9 |
| Informational | 0.0 |

Use this AI/ML interface scoring rubric when CVSS cannot be calculated precisely:

```text
Exposure:
  public or internet-reachable: +2.0
  tenant/gateway reachable: +1.5
  internal service reachable: +1.0
  unknown: +0.5

Authentication / authorization gap:
  observed absent auth: +2.0
  suspected auth coverage gap: +1.5
  weak/default credentials: +1.5
  object/tenant authorization uncertain: +1.0
  unknown: +0.5

Asset impact:
  job or runtime code execution path: +2.5
  admin/management state change: +2.0
  artifact/secret/token exposure: +2.0
  cross-tenant telemetry or metadata: +1.0
  reflected script execution in platform context: +1.5

Attack complexity and preconditions:
  low complexity, network only: +1.0
  requires user interaction: +0.5
  requires authenticated low-privilege user: +0.5
  requires admin privileges: -1.0
  destructive validation not performed: no penalty; reflect uncertainty in confidence.

Evidence confidence adjustment:
  direct unauthenticated behavior observed: +1.0
  route and deployment evidence only: +0.0
  version-only or heuristic evidence: -1.0
```

Clamp the final score to 0.0-10.0. Include a `score_rationale` field explaining the main drivers.

## Phase 1 Report

Produce one primary user-facing artifact:

```text
phase1-discovery/ai-ml-candidate-vulnerability-report.md
```

Write this report in Chinese by default. It must be the single entrypoint users should read. Do not
make detail reports or YAML files the primary output.

The Phase 1 Chinese report must include:

1. 执行摘要: scanned scope, detected components, total candidate vulnerabilities, severity distribution,
   highest-risk findings, and key caveats.
2. 候选漏洞总览: ID, title, component, affected interface, vulnerability class, severity, score,
   confidence, status, and verification priority.
3. 组件与接口枚举摘要: component, version, interface type, route/protocol, operation semantics,
   observed exposure, auth observation, sensitivity, and why it matters.
4. 边界分析摘要: candidate ID or interface ID, expected boundary, observed boundary, mismatch reason,
   affected asset, and confidence.
5. 候选漏洞详情: one section per candidate with evidence, score rationale, impact, validation preview,
   false-positive conditions, and remediation guidance.
6. Phase 2 人工验证预览: a prioritized list of what should be verified next.
7. Phase 2 验证计划: prioritized manual verification plan preview.
8. 研究模式总结: reusable boundary-mismatch patterns that can inform taxonomy and paper writing.
9. 附录: concise structured YAML blocks for components, interfaces, boundary models, candidate
   vulnerabilities, research patterns, and proposed taxonomy extensions.

Use [aiml-report-template.md](aiml-report-template.md) for the exact report tables and section
format. Do not use PoC count, confirmed exploit count, or 0-day count as the primary report frame.

## Phase 2: Verification — Detailed Instructions

Phase 2 is a manual verification plan and evidence review stage. It is not a PoC stage.

The verifier must answer five questions for each candidate:

1. Is the interface actually reachable in the platform deployment?
2. Is authentication enforced for every route stack, protocol, and HTTP method?
3. Is authorization scoped to the correct user, workspace, project, namespace, tenant, object, or
   admin role?
4. Does the interface expose sensitive data or change backend state?
5. Which evidence would confirm, falsify, or downgrade the candidate?

Produce:

```text
phase2-verification/ai-ml-manual-verification-plan.md
```

The report must include:

- 验证总览: number of candidates, priority distribution, required environment, and global safety rules.
- 验证矩阵: candidate ID, priority, environment needed, safe test available, destructive test needed,
  owner, and current status.
- One verification plan per candidate:
  - Candidate ID and title.
  - Current evidence.
  - Evidence gaps.
  - Verification priority and rationale.
  - Preconditions.
  - Safe verification steps.
  - Dangerous steps that must not be automated.
  - Expected validation signals.
  - False-positive conditions.
  - Logs, responses, configs, and code paths to collect.
  - Decision placeholder: `confirmed`, `false_positive`, `needs_more_evidence`, or `not_tested`.

Priority guidance:

- P0: Critical/High score, high confidence, unauthenticated or public/tenant-reachable, affects job
  execution, runtime access, admin management, token/secret exposure, or arbitrary code execution.
- P1: High or Medium score with clear sensitive interface but missing exposure/auth evidence.
- P2: Medium/Low score, mostly metadata/telemetry/artifact concern, or requires specific deployment
  assumptions.
- P3: Informational or weak evidence, useful for hardening but not ready for vulnerability validation.

### High-Effect Phase 2 Prompt Template

Use this prompt when assigning Phase 2 to a verifier. It works best because it constrains the agent
to reproduce the evidence chain, test the boundary hypothesis, and produce a non-destructive manual
plan instead of inventing exploits.

```text
You are a senior AI/ML platform security verifier. Your task is Phase 2 verification planning for
candidate vulnerabilities produced by an AI/ML interface-boundary scan.

Do not perform generic vulnerability hunting. Do not write exploit code. Do not run destructive
tests. Your job is to verify whether each Phase 1 candidate has enough evidence, what evidence is
missing, and what safe manual steps an authorized tester should run.

Target project or deployment evidence:
{project_path_or_evidence_path}

Phase 1 candidate report:
{report_dir}/phase1-discovery/ai-ml-candidate-vulnerability-report.md

Output path:
{report_dir}/phase2-verification/ai-ml-manual-verification-plan.md

Candidate IDs to verify:
{candidate_id_list}

For each candidate, extract or reconstruct:
1. component and version;
2. affected interface, route, method, protocol, and interface type;
3. expected boundary;
4. observed boundary;
5. current evidence;
6. evidence gaps;
7. false-positive conditions;
8. safe testing notes from Phase 1.

Then evaluate the candidate using this checklist:
1. Reachability: Is the route/interface reachable from the platform exposure model?
2. Authentication: Is identity enforced across every route stack, method, WebSocket/SSE upgrade, proxy
   path, and backend service path?
3. Authorization: Is access scoped to the correct user, workspace, project, namespace, tenant, object,
   or admin role?
4. Operation semantics: Is the interface read-only, sensitive-read, state-changing, management-plane,
   runtime-control, artifact-control, telemetry, model-serving, or storage-related?
5. Boundary mismatch: Does the observed deployment violate the component's expected trust boundary?
6. Mitigations: Is there gateway, ingress, middleware, service mesh, network policy, RBAC, object
   ownership, token validation, CSRF protection, or frontend/backend normalization that prevents the
   issue?
7. Evidence quality: Is the candidate confirmed by direct evidence, supported by route/config/source
   evidence, or only heuristic?

For safe validation steps:
- Prefer source review, route metadata, OpenAPI, gateway/ingress policy inspection, frontend route
  extraction, and read-only GET/HEAD/OPTIONS probes.
- For unauthenticated checks, use read-only endpoints only and record status, headers, redirect,
  auth challenge, response shape, and server logs.
- For WebSocket/SSE, verify handshake and auth enforcement only; do not send payloads that trigger
  runtime execution.
- For management, job, model, registry, storage, or runtime-control interfaces, identify dangerous
  operations but do not call them.

Forbidden automated actions:
- Do not submit, cancel, or delete jobs.
- Do not execute code or open a shell/kernel/terminal.
- Do not delete, mutate, upload, overwrite, register, load, unload, restart, or shut down resources.
- Do not read real user artifacts, secrets, tokens, prompts, datasets, or model files.
- Do not brute force credentials or bypass access controls outside an authorized test.

Write the report in Chinese. For every candidate, include:
- 验证结论占位: confirmed / false_positive / needs_more_evidence / not_tested
- 验证优先级: P0/P1/P2/P3
- 当前证据
- 证据缺口
- 安全验证步骤
- 禁止自动执行的危险步骤
- 预期验证信号
- 误报排除条件
- 需要收集的日志、HTTP 响应、配置、代码路径
- 是否应调整 severity, score, confidence, and why

Do not upgrade a candidate to confirmed unless the evidence proves reachability plus the relevant
authentication, authorization, exposure, or trust-boundary failure. If evidence is incomplete, keep
the status as needs_more_evidence and state exactly what is missing.
```

### Compact Phase 2 Prompt

Use this shorter version when context is tight:

```text
Use $aiml-interface-boundary-scan Phase 2.

Read:
- {report_dir}/phase1-discovery/ai-ml-candidate-vulnerability-report.md
- {project_path_or_evidence_path}

Write:
- {report_dir}/phase2-verification/ai-ml-manual-verification-plan.md

Verify candidate IDs: {candidate_id_list}

For each candidate, do not exploit. Build a Chinese manual verification plan that checks
reachability, authn, authz, operation semantics, boundary mismatch, mitigations, evidence quality,
false-positive conditions, safe read-only validation steps, forbidden dangerous steps, expected
signals, required logs/configs/responses/code paths, and final decision placeholder.

Keep candidates as needs_more_evidence unless evidence proves the interface is reachable and the
relevant boundary failure exists.
```

## Safe Testing Rules

- Do not submit jobs, execute code, delete jobs, shut down services, restart components, load/unload
  models, mutate registries, or access real user artifacts during automated discovery.
- Prefer static analysis, route metadata, OpenAPI, frontend route extraction, deployment config review,
  and non-destructive HTTP probes.
- If a potentially destructive endpoint is discovered, record it as `destructive-do-not-call`.
- For auth testing, prefer read-only endpoints and document exact request/response behavior.
- For WebSocket/SSE, record handshake and routing behavior; do not send payloads that trigger runtime
  execution.
