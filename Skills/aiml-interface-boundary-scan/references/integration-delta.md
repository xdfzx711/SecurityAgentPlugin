# Integration Delta Analysis

Compare the component-native Stage A contract with the evidence-backed Stage B integration state.
Never treat `dangerous operation exists` as a delta.

## Delta record

Create one record per bound interface and principal/path combination:

```yaml
delta_id: DELTA-KSERVE-TFS-001
interface_id: CIFACE-TFS-011
binding_id: BIND-KSERVE-TFS-001
reachability_path_id: REACH-KSERVE-TFS-001
identity_policy_path_id: IDPOL-KSERVE-TFS-001

exposure_delta:
  before:
    value: trusted-internal
    source_field: component.interfaces[].security_contract.expected_network_scope
  after:
    value: tenant-facing
    source_field: reachability_paths[].principal
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
privilege_delta:
  before:
    principal_class: operator
  after:
    principal_class: tenant-user
  changed: true
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

## Comparison rules

### Exposure

Compare expected component scope with every proven platform principal and route. Treat cluster
internal reachability as distinct from tenant-facing reachability. Do not equate ingress with public
access.

### Authentication and authorization

Separate authentication from authorization. Gateway login does not prove permission for the
specific interface, method, object, model, namespace, workflow, artifact, or management operation.

### Identity

Compare the identity assumed by the component with what it actually receives. Record loss,
reconstruction, delegation, token exchange, header trust, and shared service accounts.

### Privilege and plane

Flag semantic expansion such as:

```text
platform data-plane permission -> component management-plane operation
```

`plane_delta` is evidence for A1/A3/A8-style candidates; it is not itself a vulnerability.

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

## Candidate generation

Generate a candidate only when:

1. a concrete `CIFACE-*` is bound;
2. the reachability or non-network invocation path is evidence-backed;
3. at least one security-relevant delta exists;
4. the delta crosses or plausibly crosses a stated security boundary;
5. impact and attacker capability are concrete;
6. false-positive conditions and missing evidence are recorded.

Map the result to A1–A8. Prefer:

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

- candidate ID, title, A1–A8 taxonomy, affected versions;
- interface, binding, reachability, identity-policy, and delta IDs;
- attacker principal and prerequisites;
- component security contract vs platform state;
- specific boundary crossed and security impact;
- integration gate, root-cause owner, confidence, evidence, and gaps;
- false-positive conditions, safe verification plan, and prohibited actions;
- status: `candidate_requires_manual_validation`, `confirmed_by_non_destructive_probe`,
  `research_only`, or `rejected_contextual`.

## Normative Stage C document

Write `{report_dir}/stage-c-security-delta/security-delta.yaml`:

```yaml
schema_version: "1.0"
security_delta_map_id: SDMAP-KSERVE-TFS-001
inputs:
  component_baseline_id: CBASE-TFS-001
  integration_map_id: IMAP-KSERVE-TFS-001
deltas: []
candidate_vulnerabilities:
  - candidate_id: CAND-AIML-001
    title: <title>
    taxonomy: <A1 | A2 | A3 | A4 | A5 | A6 | A7 | A8>
    affected_versions: []
    interface_id: CIFACE-TFS-011
    binding_id: BIND-KSERVE-TFS-001
    reachability_path_id: REACH-KSERVE-TFS-001
    identity_policy_path_id: IDPOL-KSERVE-TFS-001
    delta_ids: []
    attacker_principal: <principal>
    prerequisites: []
    component_security_contract: <structured copy of Stage A contract>
    platform_integration_state: <structured references to Stage B facts>
    security_boundary_crossed: <specific boundary>
    security_impact: []
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
    interface_id: CIFACE-TFS-011
    delta_id: DELTA-KSERVE-TFS-001
    disposition: needs_evidence
    unresolved_edge_or_gap_ids: []
    promotion_condition: <evidence required before candidate generation>
rejected_items: []
analysis_status: <complete | scoped_incomplete | blocked>
analysis_gaps: []
```

Arrays contain the complete delta/candidate records defined in this reference. IDs are unique and
all foreign keys resolve to the declared Stage A/Stage B inputs. Candidates may reference only
`reachable` or evidence-sufficient `conditional` paths; unresolved critical paths belong in
`research_leads`. Evidence uses the shared evidence-object shape.

## Regression profiles

Use known cases only as blind regression targets; do not seed conclusions into the scan:

- Triton × KServe: verify that data-plane entrypoints cannot unintentionally bind model repository
  or lifecycle management interfaces.
- TensorFlow Serving × KServe: resolve each `CIFACE-*` and determine whether `ModelService`
  management operations share externally reachable paths or policies with inference.
- TensorBoard × Kubeflow: exercise dashboard, proxy, storage, and identity mappings.
- Argo Workflows / ML Metadata × Kubeflow Pipelines: exercise CRDs, controllers, ServiceAccounts,
  artifacts, databases, metadata, and other non-network interfaces.
