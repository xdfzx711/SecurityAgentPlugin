# AI/ML Component Interface Risk Taxonomy

Use this taxonomy for AI/ML third-party components integrated into GPU compute platforms. It defines
platform interface-layer risk categories for candidate generation, scoring, verification planning,
and report terminology.

This is a seed taxonomy, not an exhaustive list. Agents must identify new AI/ML platform
interface-boundary risk categories when evidence supports a concrete boundary mismatch that does not
fit A1-A8.

## A1. Management API Boundary Bypass

Definition: management-plane APIs become reachable or usable beyond their intended admin, internal,
workspace, project, namespace, or object boundary.

Affected interfaces:

- Job control APIs.
- Model load/unload and repository management APIs.
- Cluster, session, runtime, worker, scheduler, or service management APIs.

Common signals:

- Job read, search, cancel, stop, delete, submit, or logs endpoints are tenant or public reachable.
- Model load, unload, repository poll, model metadata, or model control endpoints lack admin scope.
- Dashboard backend APIs expose worker, scheduler, cluster, or runtime management actions.

Candidate vulnerability patterns:

- Potential unauthorized access to job management endpoints in `<component>`.
- Potential model repository control-plane exposure in `<component>`.
- Potential tenant-reachable cluster/session management API in `<platform route>`.

Validation focus:

- Check gateway, ingress, middleware, and backend route coverage for management paths and methods.
- Use only read-only management endpoints for unauthenticated or low-privilege checks.
- Confirm mutating operations are protected without calling them.

False-positive conditions:

- Management routes are internal-only and unreachable from tenant or public paths.
- Gateway or backend enforces admin-only authorization before the request reaches the component.
- The management feature is disabled in the deployed configuration.

## A2. Dashboard / Proxy Boundary Confusion

Definition: dashboard, reverse-proxy, path-rewrite, or upgrade-protocol behavior crosses a platform
boundary differently from the intended component boundary.

Affected interfaces:

- Dashboard routes.
- Runtime and notebook proxies.
- WebSocket, SSE, gRPC, and backend proxy routes.
- User-controlled host, path, scheme, prefix, or target parameters.

Common signals:

- Dashboard proxy bypasses platform authentication or authorization.
- WebSocket upgrade and HTTP route authentication differ.
- User-controlled host or path changes the backend target or normalized path.
- Backend component is reachable directly outside the intended proxy boundary.

Candidate vulnerability patterns:

- Potential dashboard proxy authentication bypass in `<component>`.
- Potential WebSocket authorization inconsistency in `<runtime proxy>`.
- Potential backend route confusion through user-controlled proxy path.

Validation focus:

- Compare HTTP and WebSocket/SSE authentication behavior.
- Inspect proxy path normalization, route stripping, prefix handling, and backend target selection.
- Verify direct backend service exposure and gateway policy coverage.

False-positive conditions:

- Proxy target is fixed and not user controlled.
- Upgrade protocols share the same authentication and authorization path as HTTP routes.
- Backend services are not reachable from tenant or public networks.

## A3. Runtime Execution Boundary Drift

Definition: runtime, job, notebook, kernel, backend, plugin, or model-deployment capabilities grant
execution or control privileges beyond the caller's intended platform authority.

Affected interfaces:

- Notebook kernels, terminals, sessions, and runtime proxies.
- Job submit, logs, stop, cancel, and runtime APIs.
- Model deployment, custom backend, plugin loading, and tool execution surfaces.

Common signals:

- Notebook, kernel, or job runtime operates with broader service or node privileges than the user.
- Model deployment or backend configuration becomes a path to code execution.
- Runtime logs, shells, terminals, or kernels are not scoped to the owning user or session.

Candidate vulnerability patterns:

- Potential cross-user runtime access through `<runtime interface>`.
- Potential unauthorized job execution path in `<component>`.
- Potential model deployment control leading to backend code execution in `<platform>`.

Validation focus:

- Verify owner-session, workspace, project, namespace, and runtime identity binding.
- Check whether job or notebook routes require both authentication and object-level authorization.
- Identify execution-triggering endpoints without calling them.

False-positive conditions:

- Runtime access is bound to a short-lived owner session and object-level authorization.
- Job submission and runtime control are disabled or admin-only.
- Execution interfaces are isolated in a controlled test namespace with no tenant path.

## A4. Artifact / Registry Boundary Drift

Definition: model, checkpoint, dataset, prompt, artifact URI, registry metadata, bucket, or local path
semantics drift across platform object boundaries.

Affected interfaces:

- Model and artifact registries.
- Dataset, checkpoint, prompt, and run artifact APIs.
- Object-store, local-path, `file://`, bucket URI, and registry metadata fields.

Common signals:

- `source_url`, `artifact_uri`, local path, `file://`, or bucket URI is trusted inconsistently.
- Registry tag, object type, model version, or artifact type changes validation branches.
- Read or download API joins user input with stored metadata root.
- Workspace or project checks exist for one artifact type but not another.

Candidate vulnerability patterns:

- Potential artifact read boundary bypass through registry metadata in `<component>`.
- Potential local file exposure through trusted artifact URI.
- Potential cross-workspace model or dataset access through object-store boundary drift.

Validation focus:

- Compare validation logic across artifact object types and registry operations.
- Verify local paths, file URIs, and cross-workspace buckets are rejected consistently.
- Confirm storage authorization is enforced independently from UI checks.

False-positive conditions:

- Artifact URI is canonicalized and constrained to the tenant's storage root.
- Object-store IAM prevents cross-tenant reads even if metadata is confusing.
- Registry metadata is never used as a read root or fetch target.

## A5. Telemetry / Logging Disclosure

Definition: metrics, traces, logs, statistics, or operational metadata reveal cross-tenant or
sensitive AI platform information.

Affected interfaces:

- Prometheus, DCGM, metrics, traces, and statistics APIs.
- Job, pod, node, GPU, queue, scheduler, and runtime logs.
- Model-serving request metadata and platform audit logs.

Common signals:

- Metrics expose other tenants' jobs, pods, GPUs, nodes, queue state, model names, or resource usage.
- Logs expose tokens, secrets, environment variables, model paths, artifact paths, prompts, or request
  metadata.
- Trace or statistics endpoints reveal tenant, workspace, project, or model metadata.

Candidate vulnerability patterns:

- Potential cross-tenant GPU telemetry disclosure through `<metrics endpoint>`.
- Potential job log disclosure across workspace boundaries.
- Potential model-serving request metadata leakage through tracing endpoint.

Validation focus:

- Check label dimensions, query permissions, and namespace or tenant filters.
- Use synthetic or test data only; do not read real user logs or artifacts.
- Verify log redaction for tokens, secrets, paths, prompts, and environment variables.

False-positive conditions:

- Metrics are aggregated without tenant-identifying labels or sensitive metadata.
- Logs are scoped to the owning user, workspace, or namespace.
- Sensitive fields are consistently redacted before exposure.

## A6. Deployment Default Exposure

Definition: deployment defaults expose components that assume trusted internal networks or optional
authentication.

Affected interfaces:

- Kubernetes Service, Ingress, Gateway, NodePort, LoadBalancer, port-forward, and service mesh routes.
- Helm values, Docker Compose, environment variables, default credentials, and auth flags.
- Dashboards, metrics endpoints, object stores, and model-serving control planes.

Common signals:

- NodePort or LoadBalancer exposes an internal AI/ML component.
- Dashboard or metrics endpoint is unauthenticated by default.
- Ingress/OIDC protects only the platform facade while internal service routes remain reachable.
- Component docs assume trusted-network deployment, but platform routes are tenant or public reachable.

Candidate vulnerability patterns:

- Potential public exposure of internal `<component>` dashboard.
- Potential tenant-reachable unauthenticated metrics endpoint due to service exposure.
- Potential default-auth disabled deployment of `<component>` behind incomplete gateway coverage.

Validation focus:

- Inspect Helm values, services, ingresses, gateways, network policies, and environment variables.
- Compare documented component assumptions against actual platform exposure.
- Confirm whether direct service paths bypass the authenticated facade.

False-positive conditions:

- NetworkPolicy, service mesh, firewall, or private ingress prevents tenant or public reachability.
- Authentication is enforced at a gateway that covers every backend path and protocol.
- Default credentials are disabled, rotated, or unreachable.

## A7. Identity Propagation Mismatch

Definition: caller identity, tenant, workspace, project, namespace, object, or role context is lost,
over-trusted, or inconsistently propagated between the platform gateway and AI/ML component backend.

Affected interfaces:

- Gateway-authenticated APIs.
- Backend service APIs that rely on headers, service accounts, or frontend checks.
- Storage, runtime, telemetry, dashboard, model-serving, and artifact APIs.

Common signals:

- Gateway authenticates the user, but backend only sees a service account or no user identity.
- Backend trusts `X-User`, `X-Forwarded-*`, `X-Remote-User`, namespace, project, or owner headers.
- UI performs permission checks, but native API lacks object-level authorization.
- One interface enforces workspace scope while another uses cluster-wide or service identity.

Candidate vulnerability patterns:

- Potential object-level authorization bypass due to lost user identity in `<backend>`.
- Potential forged identity header trust in `<component route>`.
- Potential UI/API authorization mismatch for `<resource type>`.

Validation focus:

- Trace identity propagation from gateway to backend middleware and object access checks.
- Verify backend rejects caller-controlled identity headers.
- Compare UI, native API, proxy, and storage authorization paths.

False-positive conditions:

- Gateway strips untrusted identity headers and injects signed or mTLS-bound identity.
- Backend enforces object-level authorization using trusted identity context.
- Service account access is constrained to the caller's namespace or workspace.

## A8. Route / Method / Protocol Policy Gap

Definition: security policy covers one route, method, protocol, or versioned API stack but misses
another semantically equivalent or newly introduced interface.

Affected interfaces:

- REST, gRPC, WebSocket, SSE, OpenAPI, dashboard backend, and static route stacks.
- GET, POST, DELETE, PATCH, OPTIONS, WebSocket upgrade, and streaming methods.
- Versioned or newly introduced component APIs.

Common signals:

- GET is protected, but DELETE, PATCH, OPTIONS, or WebSocket upgrade is not.
- REST is protected, but gRPC, WebSocket, SSE, or dashboard backend route is not.
- New component version adds a route stack, but gateway policy still matches the older path set.
- Multiple router or middleware stacks have different auth coverage.

Candidate vulnerability patterns:

- Potential route-method authentication coverage gap in `<component>`.
- Potential unprotected WebSocket/SSE route for `<runtime or dashboard interface>`.
- Potential gateway policy drift after `<component version>` introduced new routes.

Validation focus:

- Enumerate route, method, and protocol coverage from source, OpenAPI, gateway policy, and safe
  OPTIONS/HEAD checks.
- Compare auth behavior across semantically related routes.
- Verify version-specific route additions are covered by gateway and backend policy.

False-positive conditions:

- Backend middleware protects all route stacks independently of gateway policy.
- Unsupported methods return authenticated errors or are blocked before backend routing.
- New routes are disabled or admin-only in the deployed configuration.

## Additional Risk Families To Consider

The following families may become standalone categories when evidence shows they are recurring or
material in the target:

- External AI Backend / Tool Trust Confusion: external OpenAI-compatible endpoints, SSE streams,
  tool calls, function calls, plugin loading, or model responses can influence privileged platform
  actions.
- Storage / Secret Boundary Drift: object stores, mounted volumes, environment variables, connection
  settings, credentials, or service tokens cross tenant, project, workspace, or component boundaries.
- Model Serving Data Plane Confusion: inference endpoints, model metadata, batching, ensemble routing,
  or backend selection expose cross-tenant model data or control-plane behavior.
- Admin Bootstrap / First-Run Exposure: first-run setup, default admin creation, bootstrap tokens, or
  initialization routes remain reachable after deployment.
- Path Normalization Boundary Mismatch: gateway, proxy, frontend, and backend normalize encoded,
  duplicated, stripped, or rewritten paths differently.

## Adding New Risk Categories

When a candidate does not fit A1-A8, add a proposed category in the report appendix:

```yaml
risk_id: AX
name: <short name>
definition: <boundary mismatch definition>
affected_interfaces:
  - <interface type>
common_signals:
  - <observable evidence>
candidate_vulnerability_patterns:
  - Potential <specific issue> in <component/interface>
validation_focus:
  - <safe validation step>
false_positive_conditions:
  - <condition that would disprove or downgrade the risk>
```

Rules for new categories:

- Anchor the category in an interface-boundary mismatch, not a generic vulnerability class.
- Cite concrete evidence that does not fit A1-A8 cleanly.
- Keep the category reusable across components or deployments.
- Do not create a new category for a one-off implementation bug unless it reveals a broader platform
  interface-boundary pattern.
