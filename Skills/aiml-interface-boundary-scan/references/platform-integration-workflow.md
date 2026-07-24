# Platform Integration Workflow

## 1. Validate the handoff

Load the Stage A YAML and verify `schema_version`, component version/commit/image, unique
`CLISTENER-*` and `CIFACE-*` IDs, coverage status, residual gaps, and safe-probe restrictions.
Fingerprint the platform source/deployment revision separately. Record version mismatches before
analysis.

Never add a newly discovered component route directly to Stage B. Report it as a Stage A baseline
gap and leave the binding unresolved until the baseline is updated.

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

## 3. Resolve interface bindings

Create one binding for each distinct platform entrypoint, backend listener, enforcement chain, and
set of component interfaces:

```yaml
binding_id: BIND-KSERVE-TFS-001
component_baseline_id: CBASE-TFS-001
baseline_runtime_compatibility: <exact | verified_equivalent | incompatible | unknown>
component_interface_ids:
  - CIFACE-TFS-011
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
  listener_id: CLISTENER-TFS-001
  protocol: gRPC
  port: 8500
platform_entrypoint:
  route: <host/path/RPC/CRD/operation>
  protocol: <HTTP | gRPC | Kubernetes | filesystem | S3 | other>
  intended_principal: <principal>
  plane: <data | control | management | telemetry | mixed>
enforcement_chain:
  - order: 1
    kind: Gateway
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
  state: <required | optional | absent | unknown>
  mechanism: <OIDC | mTLS | token | session | other | none | unknown>
authorization:
  state: <present | absent | unknown>
  scope: <user | object | tenant | namespace | role | service | coarse | unknown>
identity:
  caller_identity: <identity>
  backend_identity: <identity>
evidence: []
evidence_gaps: []
binding_status: <resolved | partially_resolved | unresolved>
```

Do not infer path/RPC coverage solely from a shared port. Resolve router matching, prefix rewrites,
method/protocol rules, gRPC service matching, and listener registration.

## 4. Build the reachability graph

Model a path as ordered nodes and evidence-backed edges:

```text
Principal
 -> Platform Entry
 -> Ingress/Gateway
 -> Authentication
 -> AuthorizationPolicy
 -> Route/Protocol Rewrite
 -> Service
 -> Pod Port
 -> Component Listener
 -> CIFACE-ID
```

Use this record:

```yaml
reachability_path_id: REACH-KSERVE-TFS-001
binding_id: BIND-KSERVE-TFS-001
principal: <tenant-user | anonymous | platform-admin | service-account | other>
target_interface_id: CIFACE-TFS-011
nodes:
  - node_id: N1
    kind: principal
    value: tenant-user
  - node_id: N2
    kind: platform_entrypoint
    value: <route>
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
- Include alternate REST, gRPC, WebSocket, SSE, direct-cluster, controller, storage, filesystem, and
  library paths.
- Record negative evidence and blocking controls.
- Do not declare reachability when any critical edge is unresolved.

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
  - location: <gateway/backend/controller/storage>
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
authorization performed only by UI routing, and loss of tenant/object context at the backend.

## 6. Stage B exit gate

Before delta analysis:

- every candidate path references a `CIFACE-*`;
- every critical reachability edge has evidence or is marked unresolved;
- every enforcement point names the identity and resource it evaluates;
- protocol/method/path rewrites and alternate paths are included;
- Stage A coverage gaps are propagated;
- non-network bindings are handled using the same evidence standard.

Stage B remains incomplete when a port is known but the concrete interface binding is not.

## Normative Stage B document

Write `{report_dir}/stage-b-platform-integration/platform-integration.yaml`:

```yaml
schema_version: "1.0"
integration_map_id: IMAP-KSERVE-TFS-001
component_baseline:
  baseline_id: CBASE-TFS-001
  schema_version: "1.0"
  artifact: <path>
platform:
  name: KServe
  version: <version | unknown>
  git_commit: <commit | unknown>
  repository: <URL or local root>
  deployment_mode: <RawDeployment | Knative | ModelMesh | other | unknown>
  deployment_profile: <profile>
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
reachability_paths: []
identity_policy_paths: []
propagated_stage_a_gaps:
  - gap_id: CGAP-TFS-001
    affected_binding_ids: []
    affected_reachability_path_ids: []
    effect: <unresolved | conditional | confidence_reduced>
analysis_status: <complete | scoped_incomplete | blocked_version_mismatch>
analysis_gaps: []
evidence: []
```

Arrays contain the complete records defined above. All IDs are unique. Foreign keys must resolve to
this document or the named Stage A baseline. `analysis_status: complete` requires exact/verified
compatibility, no unresolved critical binding/path, and complete propagation of all Stage A gaps.
All evidence lists use the Stage A evidence-object shape, extended with platform object kind/name
and namespace in `locator` when applicable.
