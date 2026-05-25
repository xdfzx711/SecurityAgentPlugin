# AI/ML Interface Boundary Scan

Use this reference when the target is an AI/ML platform, GPU compute platform, model-serving
platform, notebook platform, MLOps stack, or a product that integrates third-party AI/ML
components such as MLflow, Ray, Jupyter, Dask, Open WebUI, Kubeflow, Triton, Prometheus, DCGM,
MinIO, or similar services.

The purpose is not to immediately claim exploitable CVEs. The purpose is to enumerate exposed
interfaces, model their expected security boundaries, identify boundary mismatches, and produce
reviewable suspicious-pattern reports with safe validation guidance.

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
Suspicious Pattern Reporter
        ->
Verification / Validation
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

## Suspicious Pattern Taxonomy

Treat the following as seed patterns, not an exhaustive list. Agents must also invent new pattern
labels when evidence shows a boundary mismatch that does not fit P1-P6. Newly introduced labels
must include a concise definition, matched evidence, impact hypothesis, and manual validation steps.

Seed patterns:

| ID | Pattern | Typical Components |
| --- | --- | --- |
| P1 | Mixed Routing Authentication Coverage Gap | MLflow, Jupyter, web apps mixing Flask/FastAPI/Tornado/WebSocket/SSE |
| P2 | Unsafe Default / Trusted-Internal Assumption | MLflow, Ray, dashboards, admin consoles |
| P3 | Artifact / Registry Semantic Reuse Mismatch | MLflow, model registries, prompt registries, object stores |
| P4 | Runtime Proxy / WebSocket Auth Inconsistency | Jupyter Server Proxy, JupyterHub, notebook gateways |
| P5 | Dashboard Management Endpoint Exposure | Ray Dashboard, Dask Dashboard, Kubeflow dashboards |
| P6 | External AI Backend Trust Confusion | Open WebUI, OpenAI-compatible connectors, tool/function platforms |

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

When creating a new pattern, use:

```yaml
pattern_id: SP-CUSTOM-<short-name>
pattern: <name>
definition: <one paragraph>
component: <component>
interface: <route/protocol>
confidence: low | medium | high
evidence:
  - <observable signal>
boundary:
  expected: <expected boundary>
  observed: <observed or suspected mismatch>
possible_platform_impact:
  - <impact hypothesis>
recommended_manual_validation:
  - <safe manual step>
safe_testing_note: <what not to trigger automatically>
```

## Seed Pattern Templates

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

## Reporting Requirements

Produce three primary artifacts during Phase 1 when this profile is selected:

```text
phase1-discovery/interface-enumeration-table.yaml
phase1-discovery/boundary-model-table.yaml
phase1-discovery/suspicious-pattern-report.md
```

Suspicious reports must avoid overstating claims. Use "suspected", "possible", and "requires
manual validation" unless the evidence proves exploitability.

Include:

- Component and version confidence.
- Interface and operation semantics.
- Expected boundary vs observed or suspected boundary.
- Evidence source and safety level.
- Possible platform impact.
- Recommended manual validation.
- Safe testing note.
- Whether the finding maps to a known seed pattern or a newly defined pattern.

## Safe Testing Rules

- Do not submit jobs, execute code, delete jobs, shut down services, restart components, load/unload
  models, mutate registries, or access real user artifacts during automated discovery.
- Prefer static analysis, route metadata, OpenAPI, frontend route extraction, and non-destructive
  HTTP probes.
- If a potentially destructive endpoint is discovered, record it as `destructive-do-not-call`.
- For auth testing, prefer read-only endpoints and document exact request/response behavior.
- For WebSocket/SSE, record handshake and routing behavior; do not send payloads that trigger runtime
  execution.
