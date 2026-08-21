# Platform Integration Workflow

## 1. Validate the handoff

Load the Stage A YAML and verify `schema_version`, component version/commit/image, unique
`CLISTENER-*` and `CIFACE-*` IDs, coverage status, residual gaps, and safe-probe restrictions.
Fingerprint the platform source/deployment revision separately. Record version mismatches before
analysis.

Never add a newly discovered component route directly to Stage B. Report it as a Stage A baseline
gap and leave the binding unresolved until the baseline is updated.

Stage A schema 3.0 is required for complete analysis because it carries workload-specific runtime
privilege contracts. Older baselines may support a scoped interface-only analysis, but all affected
runtime-privilege bindings and deltas remain unresolved; request a matching Stage A 3.0 baseline.

Classify baseline/runtime compatibility:

- `exact`: runtime image digest or source commit matches the baseline.
- `verified_equivalent`: a reproducible build/package manifest proves the same component code and
  interface-affecting profile.
- `incompatible`: version, commit, image, build features, default arguments, or configuration can
  change interfaces.
- `unknown`: evidence cannot establish equivalence.

Only `exact` or `verified_equivalent` may produce resolved bindings. For `incompatible` or `unknown`,
set all affected bindings `unresolved`, stop candidate generation for them, and require a new or
matching Stage A baseline. Do not rescan the component inside Stage B.

## 2. Locate the integration

Find every platform object that selects, starts, proxies, exposes, configures, authenticates, or
authorizes the component:

- runtime/operator/controller source;
- Deployments, StatefulSets, Pods, sidecars, Services, EndpointSlices;
- Ingress, Gateway, HTTPRoute/GRPCRoute, VirtualService, Envoy/Nginx configuration;
- Helm defaults, overlays, flags, environment variables, ports, probes;
- Authentication middleware, AuthorizationPolicy, RBAC, NetworkPolicy;
- ServiceAccounts, token forwarding, identity headers, mTLS identities;
- volumes, PVCs, object stores, artifact repositories, databases;
- CRDs, controllers, admission webhooks, and workflow templates.
- workload `securityContext`, capabilities, privileged mode, `hostNetwork`, `hostPID`, `hostIPC`,
  RuntimeClass, automounted credentials, and pod egress controls;
- `hostPath`, Unix sockets, device files, GPU/device-plugin mounts, CDI/DRA resources, DaemonSets,
  kubelet/container-runtime endpoints, node agents, and cloud metadata routes;
- service-mesh sidecar coverage and bypass conditions for Pod-to-Service, Pod-to-Pod, host-network,
  and node-local traffic.

For every component workload role, resolve its `CPRIV-*` against the effective platform grant using
[runtime-privilege-delta.md](runtime-privilege-delta.md). Include operator-generated workloads,
admission mutation, RuntimeClass/CDI/device-plugin injection, and resolved RoleBinding/
ClusterRoleBinding permissions; Helm values alone are insufficient when these layers can mutate the
result.

## 3. Resolve interface bindings

Create one binding for each distinct access entrypoint, backend listener/non-network registration
root or GPU asset, enforcement chain, and target set. An entrypoint may be an external route, a
ClusterIP or Pod IP, a node-local endpoint, a Kubernetes resource, a mounted path/device, storage,
fabric, driver/kernel interface, or library invocation:

```yaml
binding_id: BIND-KSERVE-TFS-001
component_baseline_id: CBASE-TFS-001
baseline_runtime_compatibility: <exact | verified_equivalent | incompatible | unknown>
component_interface_ids:
  - CIFACE-TFS-011
target_refs:
  - kind: component_interface
    target_id: CIFACE-TFS-011
runtime_privilege_binding_ids:
  - RPBIND-TFS-001
platform:
  name: KServe
  version: <version | unknown>
  git_commit: <commit | unknown>
integration_objects:
  - kind: ClusterServingRuntime
    name: <name>
    namespace: <namespace or cluster-scoped>
  - kind: Service
    name: <name>
    namespace: <namespace>
backend:
  listener_id: <CLISTENER-* | not_applicable>
  protocol: <gRPC | device | IPC | RDMA | ioctl | other | not_applicable>
  port: <number | not_applicable>
platform_entrypoint:
  kind: <external_route | cluster_service | pod_endpoint | node_local_endpoint |
         kubernetes_resource | filesystem | device | storage | library | other>
  locator: <host/path/RPC/service/Pod IP/socket/device/CRD/path/operation>
  protocol: <HTTP | gRPC | TCP | Unix | Kubernetes | filesystem | device | S3 | library | other>
  intended_principal: <principal>
  plane: <data | control | management | telemetry | mixed>
enforcement_chain:
  - order: 1
    kind: <Gateway | NetworkPolicy | ServiceMesh | BackendAuthn | BackendAuthz | RBAC |
           FilePermission | DevicePolicy | RuntimeIsolation | MetadataPolicy | other>
    reference: <file/object>
    selectors:
      hosts: []
      paths: []
      methods: []
      protocols: []
      grpc_services: []
      grpc_methods: []
      kubernetes_api_groups: []
      kubernetes_resources: []
      kubernetes_verbs: []
    effect: <allow | deny | route | authenticate | authorize | transform | unknown>
    precedence: <number | unknown>
    default_action: <allow | deny | no_match | unknown>
    evaluated_rule: <rule name/index | unknown>
authentication:
  state: <required | optional | absent | not_applicable | unknown>
  mechanism: <OIDC | mTLS | token | session | runtime_policy | device_policy | file_permission |
              other | none | not_applicable | unknown>
authorization:
  state: <present | absent | not_applicable | unknown>
  scope: <user | object | tenant | namespace | role | service | assigned_device | ipc_domain |
          fabric_membership | node | coarse | not_applicable | unknown>
identity:
  caller_identity: <identity>
  backend_identity: <identity>
evidence: []
evidence_gaps: []
binding_status: <resolved | partially_resolved | unresolved>
```

`target_refs` is authoritative. Preserve `component_interface_ids` as a compatibility projection of
all `component_interface` targets; it may be empty for a GPU-asset-only binding. Every `GASSET-*`
must resolve to `gpu_assets` in the same Stage B document.

Do not infer path/RPC coverage solely from a shared port. Resolve router matching, prefix rewrites,
method/protocol rules, gRPC service matching, and listener registration. Do not copy authentication
or authorization from an Ingress binding to a direct-cluster or node-local binding unless the
backend, mesh, network, filesystem, device, or runtime control is proven to cover that path.

## 4. Build the reachability graph

Model each applicable path class as ordered nodes and evidence-backed edges. The north-south shape is
only one path class:

```text
north_south:
  Principal -> Platform Entry -> Ingress/Gateway -> Policy -> Service -> Listener -> CIFACE-ID

workload_east_west:
  Tenant GPU Pod -> Egress/NetworkPolicy/Mesh -> ClusterIP/Pod IP/NodePort
  -> Backend Policy -> Listener -> CIFACE-ID

node_local:
  Tenant GPU Pod -> Pod/Host Isolation Boundary
  -> localhost/hostNetwork/Unix Socket/Device File/kubelet/Node Agent
  -> Target Interface

kubernetes_control_or_non_network:
  Tenant GPU Pod -> Mounted Credential/Filesystem/CRD/Library Call
  -> Kubernetes API/Controller/Storage/Component Registration Root -> Target Interface
```

Use this record:

```yaml
reachability_path_id: REACH-KSERVE-TFS-001
binding_id: BIND-KSERVE-TFS-001
path_class: <north_south | workload_east_west | node_local | kubernetes_control |
             non_network | storage>
principal: <tenant-user | another-tenant-user | anonymous | platform-admin | service-account |
            tenant-workload | node-local | other>
attacker_context:
  actor_class: <tenant_user | anonymous | platform_admin | service_account |
                workload_process | node_process | other>
  origin: <external_network | tenant_workload | node_local | control_plane_workload | other>
  tenant_relation: <same_tenant | another_tenant | shared_platform | not_applicable | unknown>
  initial_capabilities:
    - <arbitrary_code_in_gpu_pod | cluster_network_access | service_account_token |
       host_network_access | node_code_execution | other>
  effective_identity: <anonymous | pod_ip | workload_service_account | user_token |
                       node_identity | cloud_identity | other | unknown>
target_interface_id: <CIFACE-* | not_applicable>
target:
  kind: <component_interface | gpu_asset>
  target_id: <CIFACE-* | GASSET-*>
nodes:
  - node_id: N1
    kind: workload_origin
    value: tenant GPU Pod
  - node_id: N2
    kind: cluster_service
    value: <namespace/service:port>
edges:
  - from: N1
    to: N2
    condition: <method, host, path, protocol, policy, config>
    evidence:
      - <file/object/line>
    confidence: <high | medium | low>
status: <reachable | not_reachable | conditional | unresolved>
blocking_controls: []
evidence_gaps: []
```

Rules:

- A Service/Ingress proves only its own edge.
- A broad prefix does not prove unsupported backend methods, and a UI link is not an authorization
  control.
- Treat `arbitrary_code_in_gpu_pod` as an authorized baseline tenant capability. Do not describe it
  as a prerequisite vulnerability or require a prior container compromise.
- For every deployed component, evaluate all applicable origins: external, same-tenant workload,
  another-tenant workload, node-local workload, and service-account/control-plane workload.
- Include alternate REST, gRPC, WebSocket, SSE, ClusterIP, headless Service, Pod IP, NodePort,
  host-network, localhost, Unix-socket, device-file, IMDS, kubelet, controller, Kubernetes API,
  storage, filesystem, and library paths.
- Model same-tenant and another-tenant paths separately. A caller may arrive anonymously, by Pod IP,
  or with a ServiceAccount even when the logical actor is another tenant.
- Ingress authentication is irrelevant to a path that bypasses the Ingress unless a downstream
  control independently enforces the same identity and resource scope.
- Record negative evidence and blocking controls.
- Do not declare reachability when any critical edge is unresolved.
- If an integration-created path terminates at an accelerator device, memory context, IPC domain,
  fabric, privileged GPU agent, runtime, driver, or kernel boundary rather than a component
  interface, register an evidence-backed `GASSET-*` and target it directly. For unrelated platform
  targets outside this contract, record an unmatched research pattern and analysis gap instead of
  inventing a component interface ID.

Use `principal` only as a compatibility summary. `attacker_context` is authoritative because actor,
origin, tenant relationship, initial capability, and effective credential are distinct dimensions.
Use `target_interface_id` only as a compatibility projection for component targets; set it to
`not_applicable` for a GPU asset target.

## 5. Build the identity and policy map

For every reachable, conditional, or unresolved path, record an identity-policy entry. Use explicit
`unknown` values when a critical reachability edge prevents identity evaluation. A proven
`not_reachable` path may omit the identity-policy entry.

```yaml
identity_policy_path_id: IDPOL-KSERVE-TFS-001
reachability_path_id: REACH-KSERVE-TFS-001
caller_identity: <identity>
gateway_identity: <identity | not_applicable | unknown>
forwarded_identity: <token/header/cert/identity | absent | unknown>
backend_identity: <identity>
service_account: <name | not_applicable | unknown>
identity_preserved: <true | false | partial | unknown>
identity_lost: <true | false | unknown>
identity_reconstructed_from_header: <true | false | unknown>
header_trust:
  caller_can_supply: <true | false | unknown>
  stripped_and_reissued: <true | false | unknown>
  integrity_bound: <mTLS | signature | internal network | none | unknown>
authorization_points:
  - location: <gateway | network_policy | service_mesh | backend | kubernetes_api | controller |
               storage | filesystem | device | runtime | metadata_service | node_agent>
    policy: <reference>
    selectors:
      hosts: []
      paths: []
      methods: []
      protocols: []
      grpc_services: []
      grpc_methods: []
      kubernetes_resources: []
      kubernetes_verbs: []
    effect: <allow | deny | unknown>
    precedence: <number | unknown>
    default_action: <allow | deny | no_match | unknown>
    evaluated_rule: <rule name/index | unknown>
    subject_used: <caller | gateway | service-account | header | unknown>
    resource_scope: <object/tenant/namespace/global/unknown>
    decision: <allow/deny/conditional/unknown>
evidence: []
evidence_gaps: []
```

Explicitly detect user-to-shared-service-account collapse, caller-controlled identity headers,
authorization performed only by UI routing, loss of tenant/object context at the backend, and
workload paths that change identity from tenant code to a shared ServiceAccount, node identity, or
cloud identity. Use `gateway_identity: not_applicable` on paths that bypass the gateway; do not treat
that value as missing evidence.

## 6. Stage B exit gate

Before delta analysis:

- every candidate path has a `target` that resolves to a Stage A `CIFACE-*` or Stage B `GASSET-*`;
- every component-operation target references a concrete `CIFACE-*`; `GASSET-*` is used only for
  accelerator/node assets defined by the GPU boundary contract;
- every critical reachability edge has evidence or is marked unresolved;
- every enforcement point names the identity and resource it evaluates;
- protocol/method/path rewrites and alternate paths are included;
- every applicable tenant-workload, cross-tenant, node-local, Kubernetes-control, and non-network
  origin is evaluated or has evidence-backed `not_applicable` status;
- a protected north-south path is not used as evidence that a direct-cluster or node-local path is
  protected;
- Stage A coverage gaps are propagated;
- non-network bindings are handled using the same evidence standard.
- every deployed/default component workload role resolves to one Stage A `CPRIV-*` and one Stage B
  `RPBIND-*`, or is explicitly unresolved with an evidence gap;
- effective runtime privilege includes rendered workload, operator/admission mutation,
  RuntimeClass/CDI/device injection, and resolved ServiceAccount permissions where applicable;
- for GPU-enabled deployments, every required row in `gpu_boundary_coverage` is present and is
  `evaluated` or evidence-backed `not_applicable`.

Stage B remains incomplete when a port is known but the concrete interface binding is not, or when
an applicable tenant-workload/node-local origin has not been evaluated.

## Normative Stage B document

Write `{report_dir}/stage-b-platform-integration/platform-integration.yaml`:

```yaml
schema_version: "4.0"
integration_map_id: IMAP-KSERVE-TFS-001
component_baseline:
  baseline_id: CBASE-TFS-001
  schema_version: <"1.0" | "2.0" | "3.0">
  artifact: <path>
platform:
  name: KServe
  version: <version | unknown>
  git_commit: <commit | unknown>
  repository: <URL or local root>
  deployment_mode: <RawDeployment | Knative | ModelMesh | other | unknown>
  deployment_profile: <profile>
  gpu_enabled: <true | false | unknown>
  rendered_config_artifact: <path or unknown>
  config_revision: <digest/commit or unknown>
  runtime_component_image: <image>
  runtime_component_digest: <digest | unknown>
  evidence: []
baseline_runtime_compatibility:
  status: <exact | verified_equivalent | incompatible | unknown>
  compared_fields: []
  evidence: []
  required_action: <none | generate_matching_stage_a_baseline>
bindings: []
runtime_privilege_bindings: []
runtime_privilege_coverage:
  expected_profile_ids: []
  resolved_binding_ids: []
  unresolved_workload_roles: []
  status: <complete | incomplete>
gpu_assets:
  - asset_id: GASSET-NVIDIA-001
    kind: <physical_gpu | mig_instance | vgpu | gpu_memory_context | device_node |
           mps_daemon | ipc_namespace | shared_memory | rdma_device | collective_fabric |
           container_runtime | gpu_driver | kernel_module | privileged_daemonset | other>
    vendor: <NVIDIA | AMD | Intel | other | unknown>
    locator: <resource/device/socket/DaemonSet/module/fabric/config reference>
    node_scope: <node | node_pool | cluster | external_fabric | unknown>
    tenant_sharing: <exclusive | partitioned | time_shared | shared_service | unknown>
    allocation_mode: <full_gpu | MIG | vGPU | time_slicing | MPS | mixed | not_applicable | unknown>
    security_role: <assigned_data_device | control_device | memory_context | isolation_mechanism |
                    privileged_broker | transport | kernel_boundary | other>
    evidence: []
    evidence_gaps: []
reachability_paths: []
identity_policy_paths: []
threat_origin_coverage:
  - origin: external_network
    tenant_relation: not_applicable
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
  - origin: tenant_workload
    tenant_relation: same_tenant
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
  - origin: tenant_workload
    tenant_relation: another_tenant
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
  - origin: node_local
    tenant_relation: <same_tenant | another_tenant | shared_platform | unknown>
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
  - origin: control_plane_workload
    tenant_relation: <shared_platform | not_applicable | unknown>
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
path_class_coverage:
  - path_class: <north_south | workload_east_west | node_local | kubernetes_control |
                 non_network | storage>
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    reachability_path_ids: []
    evidence: []
gpu_boundary_coverage:
  - boundary: <device_assignment | memory_lifecycle | partition_isolation | mps_and_ipc |
               shared_memory | rdma_and_collective_fabric | privileged_gpu_agents |
               driver_and_kernel>
    applicable: <true | false | unknown>
    status: <evaluated | not_applicable | unresolved>
    asset_ids: []
    reachability_path_ids: []
    evidence: []
    evidence_gaps: []
propagated_stage_a_gaps:
  - gap_id: CGAP-TFS-001
    affected_binding_ids: []
    affected_reachability_path_ids: []
    affected_runtime_privilege_binding_ids: []
    effect: <unresolved | conditional | confidence_reduced>
analysis_status: <complete | scoped_incomplete | blocked_version_mismatch>
analysis_gaps: []
evidence: []
```

Arrays contain the complete records defined above. All IDs are unique. Foreign keys must resolve to
this document or the named Stage A baseline. `analysis_status: complete` requires Stage A schema 3.0,
exact/verified compatibility, complete runtime-privilege mapping, no unresolved critical
binding/path, complete threat-origin and path-class coverage, complete GPU boundary coverage when
`gpu_enabled: true`, and complete propagation of all Stage A gaps.
`runtime_privilege_bindings` contains the complete `RPBIND-*` records from
[runtime-privilege-delta.md](runtime-privilege-delta.md).
Create a `path_class_coverage` row for every path-class enum and a `threat_origin_coverage` row for
every relevant origin/tenant-relation combination. `not_applicable` requires evidence; omission does
not mean not applicable.
When `gpu_enabled: true`, create all eight `gpu_boundary_coverage` rows defined in
[gpu-device-node-boundary.md](gpu-device-node-boundary.md); omission means unresolved.
All evidence lists use the Stage A evidence-object shape, extended with platform object kind/name
and namespace in `locator` when applicable.
