# Integration Topology and Delegation Model

This reference extends Stage B/C for integrations that do not contain a direct source-level dependency between the declared platform and component. It is normative for `aiml-interface-boundary-scan` v6.0 and overrides older assumptions that every integration must resolve to a direct platform-to-component listener binding.

## 1. Core rule

Do not require an explicit import, package dependency, function call, embedded process, or direct network proxy between the declared platform and component.

An integration is resolved when an evidence-backed control, data, resource, or identity chain connects them through one or more of the following:

- workflow/component adapters;
- CRDs and Kubernetes controllers/operators;
- SDK or client-library calls;
- cloud service APIs;
- service accounts, workload identity, IAM roles, token exchange, or delegated credentials;
- storage/object-store handoff;
- queues/events/webhooks;
- generated manifests or controller-created resources.

The scanner must model the observed direction of control separately from the user-declared roles. A target named as `platform` may be the downstream managed execution backend while the named `component` acts as the orchestrator.

## 2. Integration topology

Create exactly one topology record for the analyzed pair.

```yaml
integration_topology:
  topology_id: TOPO-SAGEMAKER-KFP-001
  declared_roles:
    platform: Amazon SageMaker AI
    component: Kubeflow Pipelines
  observed_roles:
    orchestrator: Kubeflow Pipelines
    execution_backend: Amazon SageMaker AI
    mediators:
      - SageMaker KFP Component
      - ACK SageMaker Controller
  control_direction:
    - component_to_platform
  integration_modes:
    - workflow_adapter
    - crd_controller_delegate
    - external_managed_service
  platform_source_availability: managed_closed_source
  component_deployed_inside_platform: false
  shared_control_plane: kubernetes
  evidence: []
  evidence_gaps: []
  status: <resolved | partially_resolved | unresolved>
```

Allowed `integration_modes`:

```text
embedded_runtime
proxied_service
workflow_adapter
direct_sdk_delegate
crd_controller_delegate
external_managed_service
storage_handoff
event_driven_delegate
hybrid
other
```

Allowed `platform_source_availability`:

```text
open_source
partial
managed_closed_source
unknown
```

A managed closed-source platform is not a reason to stop Stage B. Replace unavailable implementation evidence with official API/service contracts, IAM documentation, generated SDK models, controller behavior, deployment manifests, and read-only observations. Record the evidence boundary explicitly.

## 3. Integration evidence sources

Stage B may consume multiple source roles instead of one monolithic `platform source`.

```yaml
integration_sources:
  - source_id: ISRC-SM-KFP-001
    source_role: component
    repository_or_artifact: kubeflow/pipelines
    revision: <commit>
    scope: <path>
  - source_id: ISRC-SM-KFP-002
    source_role: integration_adapter
    repository_or_artifact: kubeflow/pipelines
    revision: <commit>
    scope: components/aws/sagemaker
  - source_id: ISRC-SM-KFP-003
    source_role: controller
    repository_or_artifact: aws-controllers-k8s/sagemaker-controller
    revision: <commit>
    scope: <path>
  - source_id: ISRC-SM-KFP-004
    source_role: deployment
    repository_or_artifact: <rendered manifests / Helm / Kustomize>
    revision: <digest>
    scope: <path or object>
  - source_id: ISRC-SM-KFP-005
    source_role: service_contract
    repository_or_artifact: AWS SageMaker API documentation/model
    revision: <version/date>
    scope: CreateTrainingJob
  - source_id: ISRC-SM-KFP-006
    source_role: policy_contract
    repository_or_artifact: IAM/RBAC policy evidence
    revision: <version/date>
    scope: <policy/object>
```

Allowed `source_role` values:

```text
component
platform
integration_adapter
controller
operator
sdk
deployment
service_contract
policy_contract
storage_contract
runtime_observation
other
```

## 4. Integration bridges

Create an `IBRIDGE-*` for every mediator chain that converts one integration object or operation into another.

```yaml
integration_bridges:
  - bridge_id: IBRIDGE-SM-KFP-001
    kind: crd_controller_delegate
    source:
      participant: Kubeflow Pipelines
      object_kind: pipeline_component
      operation: create_training_job
    input_contract:
      object_kind: component_parameters
      locator: <component spec/source>
    transport:
      mechanism: kubernetes_crd
      object_kind: TrainingJob
      api_group: <group>
      version: <version>
    mediator:
      participant: ACK SageMaker Controller
      identity: <service account / cloud identity / unknown>
    sink:
      participant: Amazon SageMaker AI
      target_kind: platform_service_operation
      target_id: PSOP-SAGEMAKER-001
    transformations: []
    evidence: []
    evidence_gaps: []
    status: <resolved | partially_resolved | unresolved>
```

Allowed bridge `kind` values include the `integration_modes` plus `protocol_translation`, `resource_translation`, `identity_delegate`, and `storage_reference`.

A bridge is resolved only when every critical hop has evidence. Keyword absence in either endpoint repository is not negative evidence against an integration when adapters/controllers/contracts prove the chain.

## 5. Platform service operations

Use `PSOP-*` for concrete operations on a managed or otherwise external platform service that cannot honestly be represented as a Stage A component `CIFACE-*` or Stage B `GASSET-*`.

```yaml
platform_service_operations:
  - operation_id: PSOP-SAGEMAKER-001
    provider: AWS
    service: SageMaker
    operation: CreateTrainingJob
    plane: control
    protocol: AWS_API
    authorization_model:
      kind: IAM
      actions:
        - sagemaker:CreateTrainingJob
        - iam:PassRole
    resource_types:
      - TrainingJob
      - IAMRole
    state_changing: true
    execution_capable: true
    sensitive_read: false
    evidence: []
    evidence_gaps: []
```

Stage B/C target kinds become:

```text
component_interface   -> CIFACE-*
gpu_asset             -> GASSET-*
platform_service_operation -> PSOP-*
```

`PSOP-*` does not replace Stage A. Use it only when the security-relevant sink belongs to the platform/service side of an indirect integration.

## 6. Parameter propagation map

For workflow, SDK, controller, CRD, or managed-service integrations, trace security-sensitive user-controlled fields end to end.

```yaml
parameter_flows:
  - parameter_flow_id: PFLOW-SM-KFP-001
    source:
      participant: Kubeflow Pipelines
      object_kind: component_input
      field: roleArn
      attacker_controlled: <true | false | conditional | unknown>
      control_scope: <tenant_user | namespace_admin | platform_admin | other | unknown>
    hops:
      - order: 1
        participant: SageMaker KFP Component
        object_kind: component_parameter
        field: roleArn
        transformation: <copy | validate | normalize | default | map | drop | unknown>
      - order: 2
        participant: Kubernetes API
        object_kind: TrainingJob
        field: spec.roleArn
        transformation: copy
      - order: 3
        participant: ACK SageMaker Controller
        object_kind: desired_state
        field: RoleARN
        transformation: <copy | validate | normalize | unknown>
      - order: 4
        participant: Amazon SageMaker AI
        object_kind: CreateTrainingJobRequest
        field: RoleArn
        transformation: sink
    validation_points: []
    authorization_points:
      - kind: iam
        control: iam:PassRole
        subject: <identity>
        resource_scope: <scope>
    sink:
      target_id: PSOP-SAGEMAKER-001
      effect: execution_identity_selection
    tenant_context_preserved: <true | false | partial | unknown>
    evidence: []
    evidence_gaps: []
    status: <resolved | partially_resolved | unresolved>
```

Prioritize fields that select or reference identities, executable images, storage, networks, encryption keys, resource names, ownership tags, endpoints, models, datasets, or cross-account resources.

Common examples include:

```text
roleArn / execution role
image / imageUri / trainingImage
modelDataUrl / model artifact URI
inputDataConfig / outputDataConfig
S3 URI / bucket / prefix
KMS key
VPC / subnet / security group
job/model/endpoint name
account / region / ARN
tags / owner metadata
```

Do not treat controllability alone as a vulnerability. Resolve the validation and authorization points and the resulting authority/resource effect.

## 7. Identity chain

Replace the HTTP-centric assumption of one caller/backend identity pair with ordered identity hops whenever delegation occurs.

```yaml
identity_chains:
  - identity_chain_id: ICHAIN-SM-KFP-001
    source_principal: kubeflow-user-A
    hops:
      - order: 1
        from_identity: kubeflow-user-A
        to_identity: pipeline-runner
        mechanism: kubernetes_service_account
        transformation: identity_collapse
        context_preserved:
          user: false
          tenant: <true | false | unknown>
          namespace: <true | false | unknown>
          object_owner: <true | false | unknown>
      - order: 2
        from_identity: pipeline-runner
        to_identity: ack-sagemaker-controller
        mechanism: kubernetes_rbac
        transformation: delegated_control
        context_preserved:
          user: false
          tenant: <true | false | unknown>
          namespace: <true | false | unknown>
          object_owner: <true | false | unknown>
      - order: 3
        from_identity: ack-sagemaker-controller
        to_identity: aws-controller-role
        mechanism: workload_identity
        transformation: cloud_identity_transition
        context_preserved:
          user: false
          tenant: <true | false | unknown>
          namespace: false
          object_owner: <true | false | unknown>
      - order: 4
        from_identity: aws-controller-role
        to_identity: selected-execution-role
        mechanism: iam_passrole
        transformation: delegated_execution_identity
        context_preserved:
          user: false
          tenant: <true | false | unknown>
          namespace: false
          object_owner: <true | false | unknown>
    identity_preserved_end_to_end: <true | false | partial | unknown>
    amplification_points: []
    collapse_points: []
    authorization_points: []
    evidence: []
    evidence_gaps: []
```

Explicitly detect:

```text
identity_collapse
identity_amplification
tenant_context_loss
namespace_context_loss
object_owner_context_loss
shared_service_account
cloud_identity_transition
role_delegation
cross_account_transition
```

## 8. Resource ownership binding

Map ownership from the orchestrator/platform object model to the resulting backend resource.

```yaml
resource_bindings:
  - resource_binding_id: RBIND-SM-KFP-001
    source_owner:
      principal: user-A
      tenant: <tenant>
      namespace: namespace-A
      object_kind: PipelineRun
      object_id: run-A
    intermediate_resources:
      - kind: TrainingJobCR
        namespace: namespace-A
        name: <name>
    target_resource:
      provider: AWS
      service: SageMaker
      kind: TrainingJob
      locator: <ARN/name>
    ownership_context:
      user_preserved: <true | false | unknown>
      tenant_preserved: <true | false | unknown>
      namespace_preserved: <true | false | not_applicable | unknown>
      owner_tagged: <true | false | unknown>
      creator_identity_preserved: <true | false | unknown>
    authorization_scope:
      create: <scope>
      read: <scope>
      update: <scope>
      delete: <scope>
      reference: <scope>
      adopt: <scope | not_applicable>
    evidence: []
    evidence_gaps: []
    status: <resolved | partially_resolved | unresolved>
```

Evaluate whether another tenant/principal can read, mutate, delete, reference, adopt, or reuse a resource created through the integration. Do not infer ownership from naming conventions or tags unless an enforcement point consumes them.

## 9. Stage B exit gate additions

For indirect/delegated integrations, Stage B is incomplete until all applicable items are evaluated:

```yaml
integration_topology_resolved:
integration_bridge_resolved:
control_flow_resolved:
identity_chain_evaluated:
parameter_flow_evaluated:
resource_ownership_binding_evaluated:
managed_service_contract_covered:
```

A direct `CIFACE-*` is no longer mandatory when the evidence-backed sink is a `PSOP-*`. At least one concrete security-relevant target must exist: `CIFACE-*`, `GASSET-*`, or `PSOP-*`.

## 10. Stage C delta extensions

For applicable paths add:

```yaml
delegation_delta:
  before:
    caller_authority: <tenant/orchestrator authority>
  after:
    delegated_authority: <controller/cloud/service authority>
  authority_amplified: <true | false | unknown>
  comparison_basis: <reason>

resource_ownership_delta:
  source_owner_scope: <scope>
  target_owner_scope: <scope>
  ownership_preserved: <true | false | partial | unknown>
  cross_tenant_reference_possible: <true | false | unknown>
  comparison_basis: <reason>

parameter_authorization_delta:
  attacker_controlled_fields: []
  security_sensitive_fields: []
  validation_present: <true | false | partial | unknown>
  authorization_bound: <true | false | partial | unknown>
  authority_effects: []
  resource_effects: []
  changed: <true | false | unknown>
  comparison_basis: <reason>
```

These are delta dimensions, not new taxonomy categories.

## 11. Candidate gate additions

Retain the existing integration gate and add:

```yaml
integration_topology_resolved: <true | false | unknown>
integration_bridge_resolved: <true | false | not_applicable | unknown>
identity_chain_evaluated: <true | false | not_applicable | unknown>
parameter_flow_evaluated: <true | false | not_applicable | unknown>
resource_ownership_binding_evaluated: <true | false | not_applicable | unknown>
```

Generate a candidate only if the relevant evidence chain is resolved enough to identify a specific boundary and impact. Missing direct source-level references between the declared platform and component is never, by itself, a rejection reason.

## 12. Taxonomy mapping

Do not create A10 for delegated/cloud integrations. Prefer existing categories:

- A1: unauthorized management or lifecycle operations on backend resources;
- A3: delegated execution authority exceeds tenant runtime authority;
- A4: artifact/storage/resource-reference scope drift;
- A7: identity collapse, cloud identity transition, tenant/owner context loss;
- A8: CRD/API/controller/version/policy coverage mismatch.

Record new recurring patterns under `Unmatched Research Patterns` only when A1-A9 cannot represent the boundary failure.

## 13. SageMaker x Kubeflow Pipelines example

A valid Stage B chain may be established as:

```text
Kubeflow user / PipelineRun
  -> SageMaker KFP component parameters
  -> SageMaker custom resource
  -> Kubernetes RBAC
  -> ACK SageMaker Controller
  -> controller cloud identity
  -> SageMaker API operation
  -> SageMaker execution role / S3 / ECR / VPC resources
```

The absence of `kubeflow` references in the SageMaker controller or Python SDK does not invalidate this integration. The security questions are whether parameter, identity, authorization, and ownership context survive or expand across the chain.