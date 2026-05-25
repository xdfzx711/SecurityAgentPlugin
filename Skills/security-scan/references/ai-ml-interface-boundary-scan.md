# AI/ML Interface Boundary Scan

Use this reference when the target is an AI/ML platform, GPU compute platform, model-serving
platform, notebook platform, MLOps stack, or a product that integrates third-party AI/ML
components such as MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus, DCGM,
MinIO, or similar services.

The purpose is not to immediately claim exploitable CVEs. The purpose is to enumerate exposed
interfaces, model their expected security boundaries, identify boundary mismatches, and produce
concrete candidate vulnerabilities with severity, score, evidence, and safe manual validation
guidance.

## Core Question

When a third-party AI/ML component is integrated into a GPU/AI platform, do its API, Dashboard,
Runtime, Artifact, Telemetry, Streaming, or Management interfaces inherit a security role they
were not designed for?

Look for mismatches between:

- The component's original deployment assumptions.
- The platform's actual exposure model.
- The authentication and authorization applied by the platform.
- The trust placed in external inputs, external backends, proxy targets, artifact metadata, or
  runtime channels.

## Pipeline

Run these modules before conventional vulnerability verification:

```text
Component Fingerprinter
        ->
Interface Enumerator
        ->
Boundary Analyzer
        ->
Candidate Vulnerability Generator
        ->
Manual Verification Planning
        ->
Validation / PoC Guidance
```

## Module 1: Component Fingerprinter

Identify deployed AI/ML components, versions, entrypoints, and deployment context.

Inputs:

- Base URL, host, port, Kubernetes service, ingress, Docker Compose service, Helm values.
- HTTP responses, static assets, OpenAPI docs, version endpoints.
- Source code route definitions, frontend route definitions, package manifests, deployment files.

Output schema:

```yaml
component: MLflow
component_version: 3.x
confidence: high
evidence:
  - /api/2.0/mlflow/experiments/search route discovered
  - MLflow UI static asset detected
deployment_context:
  exposed_via: ingress | service | direct | notebook-proxy | unknown
  auth_mode: basic-auth | token | gateway | none | unknown
  platform_tenant_scope: user | workspace | namespace | project | cluster | unknown
```

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

## Module 2: Interface Enumerator

Enumerate exposed interfaces and label protocol, operation semantics, and preliminary boundary.

Prefer passive and non-destructive sources:

1. OpenAPI, docs, route metadata, frontend static route extraction.
2. Kubernetes ingress/service and Helm value inspection.
3. HEAD, OPTIONS, and safe GET probes.
4. Known route dictionaries for identified components.

Do not trigger destructive or workload-changing operations during discovery. Identify but do not
call DELETE, shutdown, submit, cancel, restart, terminate, model-load, or arbitrary code paths.

Output schema:

```yaml
component: Ray
component_version: unknown
interface_type: Job Control
endpoint_or_route: /api/jobs/*
method_or_protocol: REST
operation_semantics: submit/status/logs/stop job
expected_boundary: internal-only or authenticated user
observed_exposure: ingress-reachable | service-reachable | notebook-proxy | unknown
auth_required: challenged | allowed | redirected | forbidden | unknown
authorization_required: object-scoped | namespace-scoped | admin-only | absent | unknown
state_changing: true
sensitive_output:
  - job logs
  - runtime status
backend_state:
  - job
  - runtime
discovery_source:
  - known-route
  - openapi
  - http-options
probe_safety: passive | non-destructive | destructive-do-not-call
risk_note: Job API is a compute control-plane interface.
```

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

## Module 3: Boundary Analyzer

For each interface, compare expected boundary against observed behavior and deployment context.

Boundary record:

```yaml
component: <component name>
component_version: <version>
interface: <endpoint / route / protocol>
interface_type: <Job Control / Runtime Proxy / Artifact / Dashboard / Streaming / ...>
boundary:
  authentication: required | optional | absent | unknown
  authorization: object-scoped | namespace-scoped | workspace-scoped | admin-only | absent | unknown
  exposure: internal-only | admin-only | tenant-facing | public | unknown
  trust: trusted-internal | untrusted-external | mixed | unknown
asset:
  job_execution: none | low | medium | high
  runtime_access: none | low | medium | high
  artifact_access: none | low | medium | high
  management_effect: none | low | medium | high
  telemetry_exposure: none | low | medium | high
  credential_or_token_exposure: none | low | medium | high
mismatch:
  type: <open taxonomy label>
  confidence: low | medium | high
  reason: <why this interface appears misaligned with expected boundary>
```

Boundary dimensions:

- Authentication: Is caller identity verified on every route stack and protocol?
- Authorization: Is the caller allowed to operate on this user/project/workspace/namespace/object?
- Exposure: Is an internal-only or admin-only interface reachable through ingress, gateway, proxy, or
  tenant network?
- Trust: Are external inputs, external services, artifact metadata, dashboard parameters, or stream
  events treated as trusted?
- Runtime: Are notebooks, terminals, kernels, WebSockets, VNC, and code-server scoped to the owning
  user/session?
- Artifact: Are model/checkpoint/prompt/dataset roots bound to the correct workspace and storage
  backend?
- Management: Are delete, shutdown, cancel, restart, load, unload, and scale operations protected?
- Telemetry: Are metrics scoped so tenants cannot read other users' jobs, pods, nodes, GPUs, or
  queue state?
- External Connector: Are OpenAI-compatible endpoints, tools, function calls, and SSE events treated
  as untrusted data?

## Module 4: Candidate Vulnerability Generator

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
  - Job execution is enabled or job APIs are active.
possible_impact:
  - Unauthenticated job submit, read, search, or cancel may be possible.
  - AI workload control-plane integrity may be affected.
validation_steps:
  - Check whether auth middleware covers the FastAPI job router.
  - Test unauthenticated access only with non-destructive read/search endpoints.
  - Confirm gateway policy covers the route prefix and all methods.
safe_testing_note: Do not submit or cancel jobs during automated discovery.
false_positive_conditions:
  - Gateway authentication protects the route before traffic reaches MLflow.
  - Job execution is disabled and all job endpoints return authenticated errors.
remediation_guidance:
  - Enforce authentication and authorization on the job router.
  - Add route-level regression tests for unauthenticated access.
related_known_cases:
  - CVE-2026-0545-style auth coverage gap
```

Use candidate status values:

- `candidate_requires_manual_validation`: evidence supports a vulnerability hypothesis, but exploitability
  has not been confirmed.
- `confirmed_by_non_destructive_probe`: a safe probe confirmed the relevant boundary failure.
- `needs_more_evidence`: interface exists, but exposure/auth behavior is too uncertain for a strong claim.
- `not_a_vulnerability_contextual`: the interface is expected and protected in the observed deployment.

## Vulnerability Scoring

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

Confidence guidance:

- High: route/interface, semantics, deployment exposure, and auth or trust behavior are all supported
  by direct evidence or source-code trace.
- Medium: interface and sensitive semantics are clear, but exposure or auth behavior needs manual
  confirmation.
- Low: version, route name, config, or heuristic signal suggests a candidate, but key evidence is
  missing.

## Internal Boundary-Mismatch Heuristics

Use these as internal detection bases, not final report titles. Treat the following as seed
heuristics, not an exhaustive list. Agents must still identify candidate vulnerabilities outside
these heuristics when evidence supports a concrete vulnerability hypothesis.

Seed heuristics and candidate vulnerability mapping:

| ID | Internal Heuristic | Typical Candidate Vulnerability Classes | Typical CWE |
| --- | --- | --- | --- |
| P1 | Mixed Routing Authentication Coverage Gap | Missing Authentication, Authentication Bypass, Broken Access Control | CWE-306, CWE-287, CWE-862 |
| P2 | Unsafe Default / Trusted-Internal Assumption | Use of Default Credentials, Missing Authentication, Exposed Dangerous API | CWE-1392, CWE-798, CWE-306 |
| P3 | Artifact / Registry Semantic Reuse Mismatch | Path Traversal, Improper Limitation of Pathname, Improper Authorization, Trust Boundary Violation | CWE-22, CWE-73, CWE-862, CWE-501 |
| P4 | Runtime Proxy / WebSocket Auth Inconsistency | WebSocket Authentication Bypass, Improper Access Control to Runtime, Session Scope Bypass | CWE-306, CWE-287, CWE-862 |
| P5 | Dashboard Management Endpoint Exposure | Missing Authorization for Management Action, Improper Access Control, CSRF-adjacent State Change Exposure | CWE-862, CWE-284, CWE-352 |
| P6 | External AI Backend Trust Confusion | Cross-Site Scripting, Improper Neutralization, Confused Deputy, Untrusted Plugin/Tool Invocation | CWE-79, CWE-116, CWE-441, CWE-94 |

Examples of additional pattern families to consider:

- Cross-tenant Telemetry Disclosure: metrics reveal other tenants' pods, nodes, GPUs, jobs, prompts,
  model names, queue state, or resource usage.
- Model Serving Control-Plane Exposure: model load/unload, repository management, or model metadata
  endpoints are tenant-reachable without admin controls.
- Artifact Storage Boundary Drift: object-store buckets, local volumes, or artifact roots are shared
  across workspace boundaries.
- Gateway Path Normalization Mismatch: platform gateway and backend component normalize paths,
  encodings, prefixes, or WebSocket upgrades differently.
- Admin Bootstrap / First-Run Exposure: first-run setup, default admin creation, or bootstrap token
  endpoints remain reachable after deployment.
- Capability Amplification Through Notebook Context: a dashboard, proxy, or frontend bug becomes code
  execution because it runs inside a notebook/runtime trust context.
- Confused Identity Propagation: the gateway authenticates the user, but the backend sees service
  identity, no identity, or a forgeable header.
- Route-Method Policy Gap: auth/gateway policy protects GET/POST but omits DELETE, PATCH, WebSocket,
  SSE, or gRPC methods.
- External Tool Execution Trust Gap: model/tool/function call metadata from untrusted backends can
  trigger privileged backend actions.
- Version-Specific Security Assumption Drift: a component version introduces a new route stack or API
  but deployment policy still assumes the older interface set.

When adding a new internal heuristic, keep it short and make sure it feeds a concrete candidate
vulnerability record:

```yaml
heuristic_id: aiml_<short_name>
heuristic: <name>
definition: <one paragraph>
candidate_vulnerability_title_pattern: Potential <specific vulnerability> in <component/interface>
typical_vulnerability_class: <Missing Authentication / Broken Access Control / XSS / Path Traversal / ...>
typical_cwe:
  - CWE-XXX
signals:
  - <observable signal>
validation_focus:
  - <safe manual step>
```

## Seed Heuristic Templates

### P1: Mixed Routing Authentication Coverage Gap

Signals:

- Same service has multiple router/app/middleware stacks.
- New route stack is not clearly behind the main auth middleware.
- REST route is protected, but FastAPI/WebSocket/SSE route has unknown or absent auth.
- Job, artifact, or admin route returns data without an auth challenge.

Manual validation:

- Compare middleware coverage across route stacks.
- Test unauthenticated access only with non-destructive read/search endpoints.
- Confirm gateway per-route policy covers all path prefixes and methods.

### P2: Unsafe Default / Trusted-Internal Assumption

Signals:

- Default admin credentials or bootstrap accounts.
- Authentication disabled by default or documented as optional.
- Documentation assumes trusted or controlled network.
- Job API, Dashboard API, or Metrics API is reachable from tenant or public routes.

Manual validation:

- Verify network exposure boundary.
- Verify token, gateway, and auth settings.
- Confirm default credentials and first-run setup endpoints are disabled or rotated.

### P3: Artifact / Registry Semantic Reuse Mismatch

Signals:

- Model, prompt, artifact, checkpoint, or dataset versions share creation flow.
- `source`, `artifact_uri`, local absolute path, `file://`, bucket URI, or registry tag affects
  artifact read root.
- Object type or tag changes validation path.
- Read API joins user path with stored metadata root.

Manual validation:

- Compare validation logic across object types.
- Verify local paths, file URIs, and cross-workspace buckets are rejected consistently.
- Confirm artifact read cannot escape the expected storage backend.

### P4: Runtime Proxy / WebSocket Auth Inconsistency

Signals:

- `/proxy/`, `/terminals/`, `/api/kernels/`, `/ws/`, VNC, RStudio, or code-server routes.
- WebSocket upgrade path and HTTP path use different auth logic.
- Unauthenticated WebSocket returns 101 Switching Protocols.
- Proxied backend is directly reachable.

Manual validation:

- Compare unauthenticated HTTP and WebSocket behavior.
- Verify WebSocket upgrade requires a valid notebook session.
- Confirm proxied backend is isolated from direct tenant or public access.

### P5: Dashboard Management Endpoint Exposure

Signals:

- Dashboard route is user-facing or public.
- Dashboard includes DELETE, shutdown, cancel, restart, terminate, scale, load, or unload operations.
- Dashboard proxy reaches worker, job, serve, scheduler, or runtime backends.
- Dashboard input is reflected into pages or errors.

Manual validation:

- Enumerate routes non-destructively.
- Verify mutating endpoints require authentication and authorization.
- Confirm dashboard is isolated from notebook/runtime trust context.

### P6: External AI Backend Trust Confusion

Signals:

- User can add external OpenAI-compatible endpoint, custom model server, or external inference backend.
- SSE, streaming, tool calls, function calls, or message metadata affect frontend/backend control flow.
- External backend can influence scripts, privileged API calls, tool execution, or function execution.
- Frontend tokens are readable by same-origin script.

Manual validation:

- Inspect SSE and streaming event handling.
- Verify strict schema validation, output escaping, and trust separation.
- Confirm external model responses cannot trigger privileged platform actions.

## Phase 1 Reporting Requirements

Produce one primary user-facing artifact during Phase 1:

```text
phase1-discovery/ai-ml-candidate-vulnerability-report.md
```

Write this report in Chinese by default. It must be the single entrypoint users should read. Do not
make detail reports or YAML files the primary output. If raw intermediate artifacts are useful for
debugging, reproducibility, or later machine processing, place them under `phase1-discovery/raw/`:

```text
phase1-discovery/raw/interface-enumeration-table.yaml
phase1-discovery/raw/boundary-model-table.yaml
phase1-discovery/raw/candidate-vulnerabilities.yaml
phase1-discovery/raw/detail-reports/{agent-name}-scan-report.md
```

Do not create `raw/` unless the user asks for raw artifacts, the scan is multi-agent and needs
traceability, or the result is complex enough that preserving structured data is useful. Even when
`raw/` exists, the Chinese main report must contain enough information to stand alone.

Candidate vulnerability reports must avoid overstating claims. Do not state that a CVE exists or
that exploitation is confirmed unless evidence proves it. Use candidate status values and make the
manual validation requirement explicit.

The Phase 1 Chinese report must include:

1. 执行摘要: scanned scope, detected components, total candidate vulnerabilities, severity distribution,
   highest-risk findings, and key caveats.
2. 候选漏洞总览表: ID, title, component, affected interface, vulnerability class, severity, score,
   confidence, status, and verification priority.
3. 组件与接口枚举摘要: component, version, interface type, route/protocol, operation semantics,
   observed exposure, auth observation, sensitivity, and why it matters.
4. 边界分析摘要: candidate ID or interface ID, expected boundary, observed boundary, mismatch reason,
   affected asset, and confidence.
5. 候选漏洞详情: one section per candidate with evidence, score rationale, impact, validation preview,
   false-positive conditions, and remediation guidance.
6. Phase 2 人工验证预览: a short prioritized list of what should be verified next.
7. 附录: embedded structured YAML blocks for candidate vulnerabilities, interface enumeration, and
   boundary analysis. Keep the appendix concise; it should support review, not replace the prose report.

Chinese Markdown report template:

```markdown
# AI/ML 第三方组件接口安全审计报告

## 1. 执行摘要

本次扫描识别到 {component_count} 个 AI/ML 组件、{interface_count} 个接口，并生成
{candidate_count} 个候选漏洞。候选漏洞仍需人工验证，不应直接视为已确认漏洞。

| 严重等级 | 数量 |
| --- | --- |
| Critical | {critical_count} |
| High | {high_count} |
| Medium | {medium_count} |
| Low | {low_count} |

## 2. 候选漏洞总览

| ID | 候选漏洞 | 组件 | 影响接口 | 漏洞类型 | 严重等级 | 分数 | 置信度 | 验证优先级 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAND-AIML-001 | 疑似 MLflow Job Control 接口未认证访问 | MLflow | `/ajax-api/3.0/jobs/*` | Missing Authentication / Broken Access Control | High | 8.1 | High | P0 |

## 3. 组件与接口枚举摘要

| 组件 | 版本 | 接口类型 | 路由/协议 | 操作语义 | 观察暴露范围 | 认证观察 | 敏感性说明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| MLflow | 3.x | Job Control | `/ajax-api/3.0/jobs/*` / REST | submit/read/search/cancel jobs | service-reachable | unknown | 任务控制面接口，可能影响工作负载完整性 |

## 4. 边界分析摘要

| 关联候选漏洞 | 组件/接口 | 预期边界 | 观察边界 | 边界失配原因 | 影响资产 | 置信度 |
| --- | --- | --- | --- | --- | --- | --- |
| CAND-AIML-001 | MLflow `/ajax-api/3.0/jobs/*` | 已认证且授权的任务控制接口 | 新路由认证覆盖未知 | FastAPI route 可能未继承 basic-auth 链路 | job_execution | High |

## 5. 候选漏洞详情

### CAND-AIML-001：疑似 MLflow Job Control 接口未认证访问

- 严重等级：High
- 评分：8.1
- 置信度：High
- 状态：candidate_requires_manual_validation
- 组件：MLflow 3.x
- 影响接口：`/ajax-api/3.0/jobs/*`（GET/POST，Job Control）
- 漏洞类型：Missing Authentication / Broken Access Control
- CWE：CWE-306, CWE-862

#### 证据
- 发现 FastAPI job route。
- 该 route 具有任务提交、读取、搜索或取消语义。
- 部署中疑似启用 basic-auth。

#### 边界失配
- 预期边界：任务控制接口应要求认证和授权。
- 观察边界：FastAPI job route 可能未共享主 basic-auth 路由链路。

#### 评分依据
- 暴露范围：service reachable。
- 认证/授权：疑似认证覆盖缺口。
- 资产影响：job-control operation。
- 置信度调整：未执行破坏性或改变状态的未认证测试。

#### 可能影响
- 未认证 submit/read/search/cancel job 可能成立。
- AI 工作负载控制面完整性可能受影响。

#### 人工验证预览
- 检查 auth middleware 是否覆盖 FastAPI job router。
- 仅使用非破坏性 read/search endpoint 做未认证访问验证。
- 确认 gateway policy 覆盖 route prefix 和所有 HTTP methods。

#### 误报条件
- Gateway 在流量到达组件前已经强制认证。
- 该 endpoint 在实际部署中被禁用或会返回认证错误。

#### 修复建议
- 对受影响 router 强制认证和授权。
- 增加跨 route stack、跨 HTTP method 的未认证访问回归测试。

## 6. Phase 2 人工验证预览

| 优先级 | 候选漏洞 | 需要补充的关键证据 | 推荐验证方式 |
| --- | --- | --- | --- |
| P0 | CAND-AIML-001 | 未认证 read/search endpoint 的响应行为；gateway per-route policy | 在授权测试环境中使用非破坏性请求验证认证 challenge |

## 7. 附录：结构化结果摘要

```yaml
candidate_vulnerabilities:
  - vulnerability_id: CAND-AIML-001
    title: 疑似 MLflow Job Control 接口未认证访问
    severity: high
    score: 8.1
```
```

## Phase 2 Manual Verification Plan

When Phase 2 is selected, produce:

```text
phase2-verification/ai-ml-manual-verification-plan.md
```

This report is not a PoC report and must not require destructive testing. It is a concrete plan for
the user or an authorized tester to validate each candidate vulnerability.

Write Phase 2 in Chinese by default. Include:

1. 验证总览: number of candidates, priority distribution, required environment, and global safety rules.
2. 验证优先级: P0, P1, P2, P3.
3. 每个候选漏洞的验证计划:
   - 候选漏洞 ID and title.
   - 当前证据.
   - 证据缺口.
   - 验证优先级 and rationale.
   - 前置条件.
   - 安全验证步骤.
   - 禁止自动执行的危险步骤.
   - 预期验证信号.
   - 误报排除条件.
   - 需要收集的日志/响应/配置.
   - 验证结论占位: confirmed / false_positive / needs_more_evidence / not_tested.
4. 验证矩阵: candidate ID, priority, environment needed, safe test available, destructive test needed,
   owner, and current status.

Priority guidance:

- P0: Critical/High score, high confidence, unauthenticated or public/tenant-reachable, affects job
  execution, runtime access, admin management, token/secret exposure, or arbitrary code execution.
- P1: High or Medium score with clear sensitive interface but missing exposure/auth evidence.
- P2: Medium/Low score, mostly metadata/telemetry/artifact concern, or requires specific deployment
  assumptions.
- P3: Informational or weak evidence, useful for hardening but not ready for vulnerability validation.

Phase 2 template:

```markdown
# AI/ML 第三方组件候选漏洞人工验证计划

## 1. 验证总览

本报告基于 Phase 1 候选漏洞生成，不直接执行破坏性验证。所有步骤应在授权测试环境中执行。

| 优先级 | 数量 | 说明 |
| --- | --- | --- |
| P0 | {p0_count} | 最高优先级，建议最先验证 |
| P1 | {p1_count} | 高优先级，需要补充关键证据 |
| P2 | {p2_count} | 中等优先级，依赖部署条件 |
| P3 | {p3_count} | 低优先级或证据不足 |

## 2. 验证矩阵

| ID | 候选漏洞 | 优先级 | 需要环境 | 是否存在安全验证步骤 | 当前状态 |
| --- | --- | --- | --- | --- | --- |
| CAND-AIML-001 | 疑似 MLflow Job Control 接口未认证访问 | P0 | 可访问 MLflow 测试实例 | 是 | not_tested |

## 3. 候选漏洞验证计划

### CAND-AIML-001：疑似 MLflow Job Control 接口未认证访问

- 验证优先级：P0
- 优先级依据：High severity、High confidence、job-control interface、认证覆盖疑似缺口。
- 当前证据：
  - 发现 `/ajax-api/3.0/jobs/*` route。
  - route 具有 job-control 语义。
- 证据缺口：
  - 未确认未认证请求是否会被 challenge。
  - 未确认 gateway 是否对该 route 单独强制认证。
- 前置条件：
  - 拥有授权测试环境。
  - 能观察 HTTP response、gateway policy 和服务端日志。
- 安全验证步骤：
  1. 使用未认证请求访问只读 read/search endpoint。
  2. 记录 HTTP status、response body、headers 和 authentication challenge。
  3. 对比受保护 REST endpoint 的未认证响应。
  4. 检查 gateway/ingress policy 是否覆盖该 path prefix 和 HTTP method。
- 禁止自动执行：
  - 不提交 job。
  - 不 cancel/delete job。
  - 不执行任意代码。
- 预期验证信号：
  - 若未认证 read/search 返回业务数据，则候选漏洞倾向 confirmed。
  - 若返回 401/403 或 gateway redirect，则倾向 false positive 或 mitigated。
- 误报排除条件：
  - gateway 已强制认证。
  - job execution disabled。
  - endpoint 仅在内部网络且不可被租户访问。
- 需要收集的证据：
  - HTTP request/response 摘要。
  - route/middleware 配置。
  - gateway/ingress policy。
  - 组件版本。
- 验证结论：not_tested
```

## Safe Testing Rules

- Do not submit jobs, execute code, delete jobs, shut down services, restart components, load/unload
  models, mutate registries, or access real user artifacts during automated discovery.
- Prefer static analysis, route metadata, OpenAPI, frontend route extraction, and non-destructive
  HTTP probes.
- If a potentially destructive endpoint is discovered, record it as `destructive-do-not-call`.
- For auth testing, prefer read-only endpoints and document exact request/response behavior.
- For WebSocket/SSE, record handshake and routing behavior; do not send payloads that trigger runtime
  execution.
