# Integration Delta Analysis

Compare the component-native Stage A contract with the evidence-backed Stage B integration state.
For a `GASSET-*` target, compare the platform/component/vendor intended isolation contract with the
effective integration state while retaining the Stage A component as the integration cause/context.
Never treat `dangerous operation exists` or `privileged GPU asset exists` as a delta.

## Delta record

Create one record per bound interface and principal/path combination:

```yaml
delta_id: DELTA-KSERVE-TFS-001
target:
  kind: <component_interface | gpu_asset>
  target_id: <CIFACE-* | GASSET-*>
interface_id: <CIFACE-* | null>
binding_id: BIND-KSERVE-TFS-001
reachability_path_id: REACH-KSERVE-TFS-001
identity_policy_path_id: IDPOL-KSERVE-TFS-001
attacker_context: <structured copy of reachability_paths[].attacker_context>

exposure_delta:
  before:
    value: trusted-internal
    source_field: component.interfaces[].security_contract.expected_network_scope
  after:
    value: tenant-facing
    origin: tenant_workload
    tenant_relation: another_tenant
    path_class: workload_east_west
    source_field: reachability_paths[].attacker_context
  changed: true
  comparison_basis: <why the values are comparable>
authentication_delta:
  before:
    value: externalized
    source_field: component.interfaces[].security_contract.built_in_authn
  after:
    state: required
    mechanism: OIDC
    source_field: bindings[].authentication
  changed: false
  comparison_basis: <reason>
authorization_delta:
  before:
    value: absent
    intended_consumer: operator
    source_field: component.interfaces[].security_contract
  after:
    state: present
    scope: coarse
    evaluated_principal: tenant-user
    source_field: bindings[].authorization
  changed: true
  comparison_basis: <reason>
identity_delta:
  before:
    intended_consumer: platform-service
    source_field: component.interfaces[].security_contract.intended_consumer
  after:
    identity_preserved: false
    backend_identity: <service account>
    source_field: identity_policy_paths[]
  changed: true
  comparison_basis: <reason>
caller_privilege_delta:
  before:
    principal_class: operator
  after:
    actor_class: tenant_user
    origin: tenant_workload
    initial_capability: arbitrary_code_in_gpu_pod
    effective_identity: workload_service_account
  changed: true
  comparison_basis: <reason>
gpu_device_delta:
  before:
    assigned_scope: <component/platform expected device scope>
  after:
    effective_devices: []
    control_devices: []
    runtime_enforcement: <enforced | absent | partial | unknown>
  changed: <true | false | unknown>
  comparison_basis: <resource request -> plugin -> CDI/runtime -> mount/device-policy evidence>
partition_isolation_delta:
  before:
    expected_tenant_boundary: <exclusive | same_tenant_shared | cross_tenant_allowed | unknown>
  after:
    mode: <full_gpu | MIG | vGPU | time_slicing | MPS | mixed | unknown>
    memory: <isolated | shared | unknown>
    control_interface: <isolated | shared | unknown>
    fault_domain: <isolated | shared | unknown>
  changed: <true | false | unknown>
  comparison_basis: <reason>
gpu_memory_lifecycle_delta:
  before:
    expected_reuse_scope: <workload | tenant | unknown>
  after:
    reuse_scope: <same_workload | same_tenant | cross_tenant | unknown>
    reset_between_allocations: <true | false | unknown>
    zeroization_guarantee: <documented | observed | absent | unknown>
  changed: <true | false | unknown>
  comparison_basis: <reason>
ipc_isolation_delta:
  before:
    expected_scope: <process | pod | tenant | unknown>
  after:
    mps_scope: <workload | tenant | cross_tenant | not_applicable | unknown>
    ipc_namespace: <private | shared_pod | host | unknown>
    shared_memory_scope: <container | pod | host | cross_tenant | unknown>
  changed: <true | false | unknown>
  comparison_basis: <reason>
fabric_trust_delta:
  before:
    expected_membership: <workload | tenant | trusted_fabric | unknown>
  after:
    rdma_scope: <dedicated | tenant_shared | cross_tenant | unknown>
    collective_membership_enforced: <true | false | unknown>
    transport_protection: <authenticated | segmented | trusted_fabric_only | none | unknown>
  changed: <true | false | unknown>
  comparison_basis: <reason>
runtime_privilege_delta:
  component_privilege_profile_id: <CPRIV-* | not_applicable>
  runtime_privilege_binding_id: <RPBIND-* | not_applicable>
  before:
    minimum_required: <structured Stage A privilege set | not_applicable>
    component_default_requested: <structured Stage A privilege set | not_applicable>
  after:
    platform_effective_granted: <structured Stage B privilege set | not_applicable>
  expansion:
    privileged_added: <true | false | not_applicable | unknown>
    allow_privilege_escalation_added: <true | false | not_applicable | unknown>
    root_execution_added: <true | false | not_applicable | unknown>
    added_capabilities: []
    added_host_namespaces: []
    added_host_mounts: []
    broadened_host_mounts: []
    added_device_access: []
    broadened_device_scope: []
    service_account_token_added: <true | false | not_applicable | unknown>
    added_service_account_permissions: []
    rbac_scope_expansion: []
    weakened_runtime_controls: []
  comparison:
    exceeds_minimum_required: <true | false | not_applicable | unknown>
    exceeds_component_default: <true | false | not_applicable | unknown>
    required_features_enabled: []
    excess_privileges_justified: <true | false | not_applicable | unknown>
  changed: <true | false | not_applicable | unknown>
  material_security_expansion: <true | false | not_applicable | unknown>
  evidence: []
  evidence_gaps: []
driver_attack_surface_delta:
  before:
    expected_driver_scope: <assigned_device | brokered | none | unknown>
  after:
    driver_version: <version | unknown>
    reachable_device_nodes: []
    reachable_interface_families: []
    supported_affected_version: <true | false | unknown>
  changed: <true | false | unknown>
  comparison_basis: <reason>
configuration_delta:
  before:
    profile: <Stage A default_runtime_profile>
  after:
    profile: <Stage B rendered platform profile>
  changed: true
  comparison_basis: <specific flags/env/mount differences>
protocol_delta:
  before:
    protocol: gRPC
    operation: <Stage A path_or_rpc>
  after:
    protocol: <gRPC | HTTP | other>
    operation: <Stage B entrypoint and rewrite>
  changed: <true | false | unknown>
  comparison_basis: <translation or policy relationship>
storage_delta:
  before:
    scope: <component storage scope>
    identity: <component expected identity>
  after:
    scope: <mounted/shared/platform storage scope>
    identity: <platform storage identity>
  changed: <true | false | unknown>
  comparison_basis: <reason>
plane_delta:
  component: management
  platform_entrypoint: data
  changed: true

integration_gate:
  integration_induced: <true | false | partially | unknown>
  present_in_standalone_equally: <true | false | unknown>
  default_or_recommended_integration: <true | false | unknown>
  requires_explicit_insecure_config: <true | false | unknown>
  low_privilege_reachable: <true | false | unknown>
  tenant_workload_origin_evaluated: <true | false | unknown>
  gpu_boundary_coverage_complete: <true | false | not_applicable | unknown>
  runtime_privilege_profiles_mapped: <true | false | unknown>
  runtime_privilege_expanded: <true | false | not_applicable | unknown>
  security_boundary_crossed: <true | false | unknown>
  documented_behavior: <true | false | unknown>
  supported_version_affected: <true | false | unknown>
  root_cause_owner: <platform | component | both | deployment | unknown>

evidence: []
evidence_gaps: []
confidence: <high | medium | low>
disposition: <candidate | research_only | rejected | needs_evidence>
disposition_reason: <reason>
```

`identity_policy_path_id` is an existing `IDPOL-*` ID for reachable, conditional, and unresolved
paths; it may be `null` only for a proven `not_reachable` path. Preserve Stage A enum values in every
`before` field. Use the corresponding Stage B field's enum in `after`; when the two domains differ,
add `comparison_basis` explaining the semantic mapping. Never invent a combined free-form state.
Each GPU-specific delta section accepts either its structured mapping or the literal
`not_applicable`; use the latter for records unrelated to accelerator/device/node boundaries.

## Comparison rules

### Exposure

Compare expected component scope with every proven actor, origin, tenant relationship, credential,
and path class. Treat cluster internal reachability from tenant-controlled workloads as
tenant-facing even when no Ingress exists. Keep same-tenant, another-tenant, shared-platform,
node-local, and public exposure distinct. Do not equate Ingress with public access or absence of
Ingress with isolation.

### Authentication and authorization

Separate authentication from authorization. Gateway login does not prove permission for the
specific interface, method, object, model, namespace, workflow, artifact, or management operation.

### Identity

Compare the identity assumed by the component with what it actually receives. Record loss,
reconstruction, delegation, token exchange, header trust, and shared service accounts.

### Caller privilege, component runtime privilege, and plane

Flag semantic expansion such as:

```text
platform data-plane permission -> component management-plane operation
```

`plane_delta` is evidence for A1/A3/A8-style candidates; it is not itself a vulnerability.

`caller_privilege_delta` compares who can invoke a target. `runtime_privilege_delta` independently
compares the component workload's Stage A minimum/default privilege contract with the Stage B
effective platform grant. Apply [runtime-privilege-delta.md](runtime-privilege-delta.md) for
normalization, comparison, ownership, and candidate rules. Do not use caller authority as a proxy
for component process privilege or vice versa.

Arbitrary code inside a tenant GPU workload is a baseline product capability. It satisfies a
realistic low-privilege starting condition; it is not a prior compromise to list as an extra exploit
prerequisite. Record any additional credential, host, node, or control-plane capability separately.

### Configuration

Compare component defaults with platform defaults or recommended manifests. Distinguish:

- secure-by-default platform behavior;
- default/recommended exposure;
- explicit insecure opt-in;
- deployment-specific drift.

### Protocol

Compare REST, gRPC, WebSocket, SSE, controller events, and versioned stacks independently. Include
method matching, path normalization, translation, reflection, upgrades, and policy coverage.

### Storage

Compare ownership and scope across PVCs, mounted paths, object-store prefixes/buckets, databases,
artifact repositories, and service credentials. Record whether platform identity broadens component
access.

### Accelerator device and node

Apply [gpu-device-node-boundary.md](gpu-device-node-boundary.md). Compare the intended accelerator,
memory, partition, IPC, fabric, privileged-broker, runtime, driver, and kernel boundary with the
effective rendered integration. Use the GPU-specific delta fields only when applicable and preserve
`unknown` rather than inferring isolation from a resource name, environment variable, sharing-mode
name, device mount, or privileged DaemonSet alone.

An A9 candidate requires a concrete `GASSET-*`, an evidence-backed tenant-workload path, a specific
expected isolation contract, observed enforcement or a critical evidence gap, and a plausible
boundary crossing. Inventory-only signals remain Stage B observations or Stage C research leads.

## Candidate generation

Generate a candidate only when:

1. a concrete Stage A `CIFACE-*` or Stage B `GASSET-*` target is bound;
2. the reachability or non-network invocation path is evidence-backed;
3. at least one security-relevant delta exists;
4. the delta crosses or plausibly crosses a stated security boundary;
5. impact and attacker capability are concrete;
6. false-positive conditions and missing evidence are recorded.

For GPU platforms, candidate generation is incomplete until applicable tenant-workload and
node-local origins have been evaluated. A gateway-protected north-south path cannot disprove a
candidate reachable through ClusterIP, Pod IP, node-local, Kubernetes-control, storage, or
non-network paths.

For every candidate involving a deployed component workload, resolve its `CPRIV-*` and `RPBIND-*`.
Runtime over-privilege alone remains an observation or research lead unless a tenant-reachable or
tenant-controlled path, concrete boundary expansion, integration relevance, and plausible security
impact are also established.

Map the result to A1–A9. Prefer:

```text
integration_induced = true
AND security_boundary_crossed = true
AND requires_explicit_insecure_config = false
AND supported_version_affected = true
```

If `present_in_standalone_equally = true` and the platform neither expands reachability nor changes
identity, privilege, policy, protocol, configuration, plane, or storage, reject it as an integration
candidate. If evidence is suggestive but a critical edge is unresolved, create a Stage C
`research_lead` with `disposition: needs_evidence`; do not place it in `candidate_vulnerabilities`
or score it as a candidate until the edge is resolved.

## Candidate output fields

Each Stage C candidate must include:

- candidate ID, title, A1–A9 taxonomy, affected versions;
- target, optional component interface, binding, reachability, identity-policy, and delta IDs;
- component runtime privilege profile/binding IDs when a deployed workload is involved;
- structured attacker context, compatibility-summary principal, and prerequisites beyond the
  platform-granted tenant workload capability;
- component security contract vs platform state;
- specific boundary crossed and security impact;
- integration gate, root-cause owner, confidence, evidence, and gaps;
- false-positive conditions, safe verification plan, and prohibited actions;
- status: `candidate_requires_manual_validation`, `confirmed_by_non_destructive_probe`,
  `research_only`, or `rejected_contextual`.

## Normative Stage C document

Write `{report_dir}/stage-c-security-delta/security-delta.yaml`:

```yaml
schema_version: "4.0"
security_delta_map_id: SDMAP-KSERVE-TFS-001
inputs:
  component_baseline_id: CBASE-TFS-001
  integration_map_id: IMAP-KSERVE-TFS-001
deltas: []
candidate_vulnerabilities:
  - candidate_id: CAND-AIML-001
    title: <title>
    taxonomy: <A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8 | A9>
    affected_versions: []
    target:
      kind: <component_interface | gpu_asset>
      target_id: <CIFACE-* | GASSET-*>
    interface_id: <CIFACE-* | null>
    binding_id: BIND-KSERVE-TFS-001
    reachability_path_id: REACH-KSERVE-TFS-001
    identity_policy_path_id: IDPOL-KSERVE-TFS-001
    delta_ids: []
    component_privilege_profile_id: <CPRIV-* | not_applicable>
    runtime_privilege_binding_id: <RPBIND-* | not_applicable>
    attacker_principal: <principal>
    attacker_context:
      actor_class: <tenant_user | anonymous | platform_admin | service_account |
                    workload_process | node_process | other>
      origin: <origin>
      tenant_relation: <tenant relationship>
      initial_capabilities: []
      effective_identity: <identity>
    prerequisites: []
    component_security_contract: <structured copy of Stage A contract | not_applicable>
    platform_integration_state: <structured references to Stage B facts>
    security_boundary_crossed: <specific boundary>
    security_impact: []
    a9_subtype: <device_assignment_exposure | gpu_memory_remanence |
                 partition_isolation_failure | shared_mps_ipc | shared_memory_ipc |
                 fabric_transport_boundary | privileged_gpu_agent_exposure |
                 driver_kernel_boundary | not_applicable>
    source_workload: <tenant workload reference | not_applicable>
    target_asset_id: <GASSET-* | not_applicable>
    expected_isolation: <structured contract | not_applicable>
    observed_enforcement: <structured state | not_applicable>
    impact_scope: <another_tenant | shared_gpu | node | cluster | fabric | not_applicable | unknown>
    critical_boundary:
      node_or_kernel_crossed: <true | false | not_applicable | unknown>
      cross_tenant_gpu_data_exposed: <true | false | not_applicable | unknown>
      shared_fabric_compromised: <true | false | not_applicable | unknown>
    integration_gate: <structured gate from delta record>
    root_cause_owner: <platform | component | both | deployment | unknown>
    confidence: <high | medium | low>
    evidence: []
    evidence_gap_ids: []
    false_positive_conditions: []
    safe_verification_steps: []
    prohibited_actions: []
    status: <candidate_requires_manual_validation | confirmed_by_non_destructive_probe | research_only | rejected_contextual>
research_leads:
  - lead_id: LEAD-AIML-001
    target:
      kind: <component_interface | gpu_asset>
      target_id: <CIFACE-* | GASSET-*>
    interface_id: <CIFACE-* | null>
    delta_id: DELTA-KSERVE-TFS-001
    component_privilege_profile_id: <CPRIV-* | not_applicable>
    runtime_privilege_binding_id: <RPBIND-* | not_applicable>
    disposition: needs_evidence
    unresolved_edge_or_gap_ids: []
    promotion_condition: <evidence required before candidate generation>
rejected_items: []
analysis_status: <complete | scoped_incomplete | blocked>
analysis_gaps: []
```

Arrays contain the complete delta/candidate records defined in this reference. A9 fields are
required when `taxonomy: A9` and use `not_applicable` for A1–A8. IDs are unique and
all foreign keys resolve to the declared Stage A/Stage B inputs. Candidates may reference only
`reachable` or evidence-sufficient `conditional` paths; unresolved critical paths belong in
`research_leads`. Evidence uses the shared evidence-object shape.
Every deployed-workload candidate resolves its `CPRIV-*` and `RPBIND-*`; `not_applicable` is allowed
only when no component workload privilege contract can affect the candidate.
`analysis_status: complete` requires Stage A schema 3.0, Stage B runtime privilege coverage
`complete`, and no unresolved material runtime privilege comparison.

## Regression profiles

Use known cases only as blind regression targets; do not seed conclusions into the scan:

- Triton × KServe: verify that data-plane entrypoints cannot unintentionally bind model repository
  or lifecycle management interfaces.
- TensorFlow Serving × KServe: resolve each `CIFACE-*` and determine whether `ModelService`
  management operations share externally reachable paths or policies with inference.
- TensorBoard × Kubeflow: exercise dashboard, proxy, storage, and identity mappings.
- Argo Workflows / ML Metadata × Kubeflow Pipelines: exercise CRDs, controllers, ServiceAccounts,
  artifacts, databases, metadata, and other non-network interfaces.
- GPU Operator/device plugin/runtime integration: exercise device assignment, privileged agents,
  runtime hooks, driver/kernel exposure, and effective device-policy enforcement.
- MIG/vGPU/time-slicing/MPS and distributed training profiles: exercise partition, memory lifecycle,
  IPC/shared-memory, RDMA/InfiniBand/NCCL, and GPUDirect trust boundaries without seeding a finding.
