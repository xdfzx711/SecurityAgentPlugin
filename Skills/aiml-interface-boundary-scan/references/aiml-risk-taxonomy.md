# AI/ML Component Interface Risk Taxonomy

Use this taxonomy for AI/ML third-party components integrated into GPU compute platforms. It defines
platform interface-layer risk categories for candidate generation, scoring, verification planning,
and report terminology.

This is a seed taxonomy. For the current integration pipeline, classify candidates only as A1-A9.
When evidence does not fit, record an unmatched research pattern without creating a new candidate
category; taxonomy evolution is a separate maintenance decision.

## Threat-origin rule

Apply every category to all relevant path classes, not only external HTTP paths. In GPU platforms,
tenant-authorized arbitrary code inside a GPU workload is a default low-privilege attacker origin.
Evaluate same-tenant workload, another-tenant workload, node-local, Kubernetes-control, storage, and
non-network paths even when the platform Ingress is absent or strongly authenticated. "Internal
only" is not a false-positive condition when tenant workloads can reach the internal surface.

## A1. Management API Boundary Bypass

Definition: management-plane APIs become reachable or usable beyond their intended admin, internal,
workspace, project, namespace, or object boundary.

Affected interfaces:

- Job control APIs.
- Model load/unload and repository management APIs.
- Cluster, session, runtime, worker, scheduler, or service management APIs.
- Workflow CRDs, controllers, admission webhooks, and service-account-mediated control operations.

Common signals:

- Job read, search, cancel, stop, delete, submit, or logs endpoints are tenant or public reachable.
- Model load, unload, repository poll, model metadata, or model control endpoints lack admin scope.
- Dashboard backend APIs expose worker, scheduler, cluster, or runtime management actions.

Candidate vulnerability patterns:

- Potential unauthorized access to job management endpoints in `<component>`.
- Potential model repository control-plane exposure in `<component>`.
- Potential tenant-reachable cluster/session management API in `<platform route>`.

Validation focus:

- Check gateway, ingress, direct ClusterIP/Pod IP, node-local, middleware, and backend policy coverage
  for management paths and methods.
- Use only read-only management endpoints for unauthenticated or low-privilege checks.
- Confirm mutating operations are protected without calling them.

False-positive conditions:

- Management routes are unreachable from public, tenant-workload, cross-tenant, node-local, and
  applicable control-plane paths.
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
- Verify Pod-to-Service, Pod-to-Pod, host-network, Unix-socket, and node-local paths independently.

False-positive conditions:

- Proxy target is fixed and not user controlled.
- Upgrade protocols share the same authentication and authorization path as HTTP routes.
- Backend services are not reachable from tenant workloads, other tenants, node-local callers, or
  public networks.

## A3. Runtime Execution Boundary Drift

Definition: runtime, job, notebook, kernel, backend, plugin, or model-deployment capabilities grant
execution or control privileges beyond the caller's intended platform authority.

Do not report the platform-granted ability to execute tenant code as the impact. Require expansion
to another tenant, a shared service, a broader ServiceAccount, the node, the control plane, or
another privilege/scope beyond the originating workload contract.

Affected interfaces:

- Notebook kernels, terminals, sessions, and runtime proxies.
- Job submit, logs, stop, cancel, and runtime APIs.
- Model deployment, custom backend, plugin loading, and tool execution surfaces.

Common signals:

- Notebook, kernel, or job runtime operates with broader service or node privileges than the user.
- Model deployment or backend configuration becomes a path to code execution.
- Runtime logs, shells, terminals, or kernels are not scoped to the owning user or session.
- Tenant workload code can reach a shared runtime, device plugin, node agent, kubelet, or mounted
  control socket with broader identity or node privileges.
- Platform-effective component privileges exceed both the Stage A minimum requirement and the
  component's default request, and tenant-controlled input reaches that workload.

Candidate vulnerability patterns:

- Potential cross-user runtime access through `<runtime interface>`.
- Potential unauthorized job execution path in `<component>`.
- Potential model deployment control leading to backend code execution in `<platform>`.

Validation focus:

- Verify owner-session, workspace, project, namespace, and runtime identity binding.
- Check whether job or notebook routes require both authentication and object-level authorization.
- Identify execution-triggering endpoints without calling them.
- Trace workload security context, device/socket mounts, ServiceAccount, host namespaces, and
  node-local endpoints before treating the runtime as isolated.
- Compare `CPRIV-*` minimum/default privileges with the rendered `RPBIND-*` effective grant using
  [runtime-privilege-delta.md](runtime-privilege-delta.md).

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
- CRDs, controllers, admission webhooks, mounted filesystems, databases, and artifact repositories.
- ClusterIP, headless Service, Pod IP, host-network, Unix socket, device file, kubelet, node agent,
  metadata-service, and device-plugin paths reachable from tenant workloads.

Common signals:

- NodePort or LoadBalancer exposes an internal AI/ML component.
- Dashboard or metrics endpoint is unauthenticated by default.
- Ingress/OIDC protects only the platform facade while internal service routes remain reachable.
- Component docs assume trusted-network deployment, but platform routes are tenant or public reachable.
- Ingress/OIDC is protected while tenant Pods can directly reach the component Service, Pod port,
  node-local endpoint, device file, kubelet, or metadata service.
- Default or recommended platform manifests grant privileged mode, host namespaces, broad hostPath,
  device scope, capabilities, or cluster RBAC beyond the component's evidence-backed requirement.

Candidate vulnerability patterns:

- Potential public exposure of internal `<component>` dashboard.
- Potential tenant-reachable unauthenticated metrics endpoint due to service exposure.
- Potential default-auth disabled deployment of `<component>` behind incomplete gateway coverage.

Validation focus:

- Inspect Helm values, services, ingresses, gateways, network policies, and environment variables.
- Compare documented component assumptions against actual platform exposure.
- Confirm whether direct service paths bypass the authenticated facade.
- Inspect workload egress, namespace selectors, sidecar bypasses, host namespaces, hostPath/device
  mounts, automounted credentials, and node-local endpoint controls.
- Distinguish component-default requests from platform-added effective privilege; resolve admission,
  RuntimeClass/CDI/device injection, and ServiceAccount RBAC before assigning ownership.

False-positive conditions:

- NetworkPolicy, service mesh, firewall, runtime isolation, file/device permissions, and node/cloud
  controls prevent every applicable tenant-workload, cross-tenant, node-local, and public path.
- Authentication and authorization are independently enforced at every reachable entrypoint and
  backend path; gateway-only enforcement does not satisfy this condition for bypass paths.
- Default credentials are disabled, rotated, or unreachable.

## A7. Identity Propagation Mismatch

Definition: caller identity, tenant, workspace, project, namespace, object, or role context is lost,
over-trusted, or inconsistently propagated between the platform gateway and AI/ML component backend.

Affected interfaces:

- Gateway-authenticated APIs.
- Backend service APIs that rely on headers, service accounts, or frontend checks.
- Storage, runtime, telemetry, dashboard, model-serving, and artifact APIs.
- Kubernetes controllers and workflows that collapse user identity into a shared ServiceAccount.

Common signals:

- Gateway authenticates the user, but backend only sees a service account or no user identity.
- Backend trusts `X-User`, `X-Forwarded-*`, `X-Remote-User`, namespace, project, or owner headers.
- UI performs permission checks, but native API lacks object-level authorization.
- One interface enforces workspace scope while another uses cluster-wide or service identity.
- Tenant workload code is transformed into a shared ServiceAccount, node identity, or cloud identity
  on a direct-cluster or node-local path.
- Platform RoleBindings/ClusterRoleBindings expand a component workload beyond its Stage A
  `service_account_permissions`, including wildcard, namespace-to-cluster, secret/node/pods-exec,
  `bind`, `escalate`, or `impersonate` authority.

Candidate vulnerability patterns:

- Potential object-level authorization bypass due to lost user identity in `<backend>`.
- Potential forged identity header trust in `<component route>`.
- Potential UI/API authorization mismatch for `<resource type>`.

Validation focus:

- Trace identity propagation from gateway to backend middleware and object access checks.
- Verify backend rejects caller-controlled identity headers.
- Compare UI, native API, proxy, and storage authorization paths.
- Compare effective identity on Ingress, ClusterIP, Pod IP, Kubernetes API, filesystem/device, IMDS,
  kubelet, and node-agent paths.

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
- CRD versions/subresources, admission operations, controller watches, and translated protocols.

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

## A9. Accelerator Device / Node Isolation Boundary Failure

Definition: accelerator devices, device memory, partitions, IPC, communication fabrics, privileged
GPU infrastructure, container runtimes, drivers, or kernel interfaces become accessible beyond the
originating workload's assigned tenant/device/node contract.

Use exactly one subtype:

```text
device_assignment_exposure
gpu_memory_remanence
partition_isolation_failure
shared_mps_ipc
shared_memory_ipc
fabric_transport_boundary
privileged_gpu_agent_exposure
driver_kernel_boundary
```

Affected assets and interfaces:

- Physical GPUs, MIG instances, vGPUs, time-sliced GPUs, and GPU memory contexts.
- `/dev/nvidia*`, `/dev/dri/*`, accelerator control devices, CUDA/driver ioctl and runtime hooks.
- MPS control/socket paths, CUDA IPC, `/dev/shm`, hostIPC, and shared memory namespaces.
- RDMA/InfiniBand/RoCE devices, SR-IOV VFs, NCCL rendezvous/collective traffic, and GPUDirect paths.
- GPU Operator, device plugins, Node Feature Discovery, driver installers, monitoring agents, and
  other privileged node DaemonSets.

Common signals:

- Effective device mounts or device rules exceed the scheduler/device-plugin allocation.
- `privileged`, host namespaces, broad hostPath, control devices, runtime configuration, or shared
  ServiceAccounts materially expand tenant workload authority.
- Device memory can be reused across tenant workloads without an evidence-backed reset/zeroization
  guarantee.
- MIG/vGPU/time-slicing/MPS configuration provides weaker memory, control, fault, or telemetry
  isolation than the platform's claimed tenant boundary.
- MPS, CUDA IPC, `/dev/shm`, RDMA, or collective communication domains are shared across untrusted
  tenants without an enforcing ownership or membership boundary.
- A tenant-controlled path reaches a privileged GPU agent, driver, or kernel interface beyond the
  assigned workload contract.
- GPU Operator, device plugin, exporter, driver manager, or runtime workload receives effective
  host/device/RBAC privilege beyond its `CPRIV-*` minimum requirement.

Candidate vulnerability patterns:

- Potential cross-tenant GPU memory disclosure after device/context reuse.
- Potential access to unassigned GPU or accelerator control devices from a tenant workload.
- Potential MIG/vGPU/time-slicing isolation boundary failure across tenants.
- Potential cross-tenant MPS, CUDA IPC, or shared-memory boundary violation.
- Potential untrusted tenant participation, observation, or interference in a shared training fabric.
- Potential tenant-to-node privilege boundary crossing through a GPU agent, runtime, driver, or
  kernel interface.

Validation focus:

- Apply [gpu-device-node-boundary.md](gpu-device-node-boundary.md) and resolve the effective resource
  request -> device plugin -> CDI/runtime -> mount -> device-policy chain.
- Compare claimed and observed isolation separately for memory, compute, control, fault, telemetry,
  IPC, and fabric membership.
- Trace tenant-controlled inputs to privileged DaemonSets, sockets, CRDs/webhooks, host paths,
  drivers, and kernel interfaces without invoking mutating or crash-prone operations.
- Confirm memory-remanence behavior only with synthetic data on an authorized isolated test node.
- Resolve each privileged GPU workload's `CPRIV-*` -> `RPBIND-*` delta; do not equate a component
  manifest's request with minimum necessity.

False-positive conditions:

- Effective device/runtime enforcement limits the workload to its assigned asset and required
  control nodes without crossing a tenant or node boundary.
- The accelerator, MPS/IPC domain, shared memory, and fabric are dedicated to one trust domain or
  enforce the claimed tenant membership and lifecycle boundary.
- Privileged GPU agents have no tenant-controlled interface or mutable input, and their authority is
  required and constrained to the documented integration contract.
- Driver/device reachability exists but no over-broad access, affected-version evidence, unsafe
  integration delta, or boundary-crossing capability is established.

A9 is mandatory first-pass coverage for GPU-enabled deployments. Taxonomy alone does not determine
severity: promote evidence-backed node/kernel crossing, cross-tenant GPU data exposure, or shared
fabric compromise to the first manual-review queue; keep configuration signals without a concrete
boundary crossing as observations or research leads.

Across all categories, runtime privilege expansion without a tenant-controlled/reachable path and
plausible boundary impact is an attack-surface observation, not a vulnerability candidate.

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

## Unmatched Research Patterns

When an observed pattern does not fit A1-A9, do not create a candidate category during the scan.
Record it separately for later taxonomy maintenance:

```yaml
pattern_id: UNMATCHED-AIML-001
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

Rules:

- Anchor the category in an interface-boundary mismatch, not a generic vulnerability class.
- Cite concrete evidence that does not fit A1-A9 cleanly.
- Keep the pattern reusable across components or deployments.
- Keep it out of `candidate_vulnerabilities` until the taxonomy is deliberately revised.
