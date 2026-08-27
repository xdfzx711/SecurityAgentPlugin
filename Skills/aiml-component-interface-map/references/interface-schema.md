# Component Interface Baseline Schema

This is the normative Stage A YAML contract. Use explicit `unknown` values and `evidence_gaps`; do
not omit required fields because evidence is unavailable.

```yaml
schema_version: "3.0"
baseline_id: CBASE-TFS-001

component:
  name: TensorFlow Serving
  version: <version | unknown>
  git_commit: <commit | unknown>
  image: <image | unknown>
  image_digest: <digest | unknown>
  source_roots: []
  provenance:
    repository: <URL or local source root>
    version_evidence: []
    commit_evidence: []
    image_evidence: []
    digest_evidence: []
  build_profile:
    build_system: <Bazel | CMake | Go | Python | other | unknown>
    build_tags: []
    compile_features: []
    packaging_profile: <profile | unknown>
    evidence: []
  default_runtime_profile:
    executable: <path or target | unknown>
    default_cli_arguments: []
    default_config_files: []
    environment_defaults: {}
    evidence: []

runtime_privilege_profiles:
  - privilege_profile_id: CPRIV-TFS-001
    workload_role: <controller | daemon | server | worker | webhook | installer | exporter | other>
    deployment_profile: <default/profile name>
    enabled_features: []
    applies_to:
      listener_ids: []
      interface_ids: []
    minimum_required:
      privileged: <true | false | unknown>
      allow_privilege_escalation: <true | false | unknown>
      run_as_user: <root | non_root | specific_uid | unknown>
      capabilities:
        add: []
        drop: []
      host_namespaces:
        pid: <true | false | unknown>
        ipc: <true | false | unknown>
        network: <true | false | unknown>
      host_mounts:
        - host_path: <path>
          container_path: <path>
          access: <read_only | read_write | unknown>
          mount_propagation: <none | host_to_container | bidirectional | unknown>
          purpose: <reason>
      device_access:
        - locator: <device path or accelerator resource>
          permissions: <read | write | rw | mknod | rwm | unknown>
          scope: <assigned_device | all_devices | control_device | unknown>
          purpose: <reason>
      service_account_permissions:
        - api_groups: []
          resources: []
          verbs: []
          resource_names: []
          non_resource_urls: []
          scope: <namespace | cluster | unknown>
      automount_service_account_token: <true | false | unknown>
      runtime_controls:
        seccomp: <profile | not_required | unknown>
        apparmor: <profile | not_required | unknown>
        selinux: <type | not_required | unknown>
        read_only_root_filesystem: <true | false | unknown>
    component_default_requested:
      privileged: <true | false | unknown>
      allow_privilege_escalation: <true | false | unknown>
      run_as_user: <root | non_root | specific_uid | unknown>
      capabilities:
        add: []
        drop: []
      host_namespaces:
        pid: <true | false | unknown>
        ipc: <true | false | unknown>
        network: <true | false | unknown>
      host_mounts: []
      device_access: []
      service_account_permissions: []
      automount_service_account_token: <true | false | unknown>
      runtime_controls:
        seccomp: <profile | not_required | unknown>
        apparmor: <profile | not_required | unknown>
        selinux: <type | not_required | unknown>
        read_only_root_filesystem: <true | false | unknown>
    requirement_basis:
      - <source | specification | official_documentation | component_manifest | inference>
    evidence: []
    evidence_gaps: []

listeners:
  - listener_id: CLISTENER-TFS-001
    process: tensorflow_model_server
    surface_kind: <network | kubernetes_resource | filesystem | object_store | webhook | controller |
                   database | library_api | device | unix_socket | shared_memory | runtime_hook |
                   kernel_interface | fabric>
    protocol: <HTTP | REST | gRPC | TCP | WebSocket | SSE | Kubernetes | filesystem | S3 | SQL |
               library | Unix | ioctl | CUDA | NVML | ROCm | IPC | CDI | OCI | RDMA | NCCL | other>
    bind_address: <address | not_applicable | unknown>
    port: <number | not_applicable | unknown>
    locator: <socket, CRD, path, device, runtime hook, driver/kernel API, fabric, database, or symbol>
    enabled_by_default: <true | false | unknown>
    registration_source:
      file: <path>
      symbol: <symbol | unknown>
      lines: <line or range | unknown>
    enabled_condition: <condition | always | unknown>
    evidence: []
    evidence_gaps: []

interfaces:
  - interface_id: CIFACE-TFS-001
    listener_id: CLISTENER-TFS-001
    surface_kind: network
    interface_family: <API | Dashboard | Runtime | Model Serving | Artifact | Storage | Telemetry |
                       Streaming | Management | Auth/Admin | Proxy |
                       Orchestration / Kubernetes Control | Accelerator / Device |
                       Node Runtime | IPC / Shared Memory | Fabric / Collective |
                       Driver / Kernel | Privileged Agent>
    interface:
      name: Predict
      path_or_rpc: tensorflow.serving.PredictionService/Predict
      method: <GET | POST | RPC | reconcile | read | write | attach | allocate | ioctl | hook | other>
      service: tensorflow.serving.PredictionService
      handler_symbol: <symbol | unknown>
    registration:
      source_file: <path>
      source_symbol: <symbol | unknown>
      enabled_condition: <condition | always | unknown>
      enabled_by_default: <true | false | unknown>
    semantics:
      capability: <caller capability>
      state_changing: <true | false | unknown>
      execution_capable: <true | false | unknown>
      sensitive_read: <true | false | unknown>
    plane: <data | control | management | telemetry | mixed>
    security_contract:
      intended_consumer: <end user | operator | platform service | controller | library caller | other | unknown>
      built_in_authn: <present | absent | optional | externalized | unknown>
      built_in_authz: <object | tenant | namespace | role | assigned-device | ipc-domain |
                       fabric-membership | node | coarse | absent | externalized | unknown>
      tenant_aware: <true | false | partial | not_applicable | unknown>
      expected_network_scope: <public | tenant-facing | trusted-internal | localhost | operator-network | not_applicable | unknown>
      expected_resource_scope: <object | path | bucket | database | namespace | cluster | process |
                                library-caller | assigned-device | memory-context | ipc-domain |
                                node | fabric-membership | not_applicable | unknown>
    protection_assumption:
      value: <self-protected | externally-protected | trusted-internal | localhost-only |
              caller-enforced | device-assignment-enforced | runtime-enforced | trusted-node |
              trusted-fabric | unknown>
      evidence_type: <source | default_config | specification | official_documentation | inference | unknown>
      evidence: []
      confidence: <high | medium | low>
    dangerous_operation: <true | false | unknown>
    danger_labels: []
    automated_probe: <allowed | forbidden>
    evidence: []
    evidence_gaps: []

interface_relationships:
  - relationship_id: CIREL-TFS-001
    from_interface_id: CIFACE-TFS-REST-001
    to_interface_id: CIFACE-TFS-001
    relationship: <protocol_translation | semantic_equivalent | alias | version_successor | shares_handler | other>
    policy_equivalence_safe: <true | false | unknown>
    evidence: []

coverage:
  listeners_discovered: 0
  route_stacks_discovered: 0
  interfaces_discovered: 0
  runtime_privilege_profiles_discovered: 0
  dynamic_registration_checked: <true | false | not_applicable>
  proto_services_checked: <true | false | not_applicable>
  feature_flags_checked: <true | false | not_applicable>
  non_network_surfaces_checked: <true | false>
  accelerator_surfaces_checked: <true | false | not_applicable>
  runtime_privilege_profiles_checked: <true | false>
  reverse_search_completed: <true | false>
  cross_check_completed: <true | false>
  unmatched_top_down: 0
  unmatched_bottom_up: 0
  discovery_checks:
    - check_id: CCHECK-TFS-001
      check: <listener_discovery | router_service_discovery | handler_rpc_enumeration |
              dynamic_registration | proto_services | feature_config_flags | non_network_surfaces |
              accelerator_surfaces | runtime_privilege_profiles | reverse_search | cross_check>
      result: <pass | fail | not_applicable>
      affected_scope:
        listener_ids: []
        interface_ids: []
        privilege_profile_ids: []
        protocols: []
        surface_kinds: []
        config_profiles: []
      evidence: []
      residual_gap_ids: []
  exclusions_count: 0
  exclusions:
    - locator: <path or symbol>
      reason: <client_only | test_only | example_only | generated_duplicate | deprecated | build_excluded | other>
      evidence: []
  residual_gaps:
    - gap_id: CGAP-TFS-001
      description: <exact missing evidence or unresolved discovery path>
      affected_scope:
        listener_ids: []
        interface_ids: []
        privilege_profile_ids: []
        protocols: []
        surface_kinds: []
        config_profiles: []
        source_roots: []
      blocks_substantial_completeness: <true | false>
      evidence: []

coverage_status: <substantially_complete | incomplete>
coverage_rationale: <why the gate passed or failed>
```

## Invariants

- Every interface references one listener/registration root.
- Every runtime workload role/profile references one `CPRIV-*`; every `applies_to` foreign key
  resolves when the privilege contract is interface-specific.
- Every ID is unique and stable within a component/version lineage.
- Every version, commit, image, build, and runtime-default assertion cites provenance evidence.
- Every relationship references existing interface IDs; translation/equivalence never collapses
  protocol-distinct interfaces into one policy target.
- `plane` describes the component operation, not a future platform route.
- `security_contract` and `protection_assumption` contain no platform observation.
- `minimum_required` records only evidence-backed necessity. A component-shipped manifest belongs in
  `component_default_requested` and is not proof that the same privilege is required.
- `automated_probe` is `forbidden` for state-changing, execution-capable, lifecycle, destructive,
  webhook-triggering, or ambiguous operations.
- `coverage_status` is `incomplete` whenever an entire protocol, plugin registry, route stack,
  configuration profile, non-network registration mechanism, or applicable accelerator
  device/runtime/driver/IPC/fabric surface remains unresolved.
- `coverage_status` is `incomplete` when any component-defined default workload role or materially
  different supported profile lacks a runtime privilege profile, or an entire privilege class is
  unexamined.
- Every failed discovery check references at least one structured residual gap. Every residual gap
  identifies affected interface/privilege IDs or an affected protocol/surface/profile/source root
  so Stage B can propagate it.

## Evidence object

Every `evidence` list in this schema contains objects, not free-form strings:

```yaml
- evidence_id: EVID-TFS-001
  evidence_type: <source | default_config | specification | official_documentation | generated_artifact | inference>
  repository_or_artifact: <repository, image, rendered config, or document>
  revision: <commit, version, image digest, or document version>
  locator: <file/object/URL>
  selector: <line range, symbol, rule, YAML path, section, or request metadata>
  assertion: <fact supported by this evidence>
  confidence: <high | medium | low>
```

For `evidence_type: inference`, cite the underlying evidence IDs in `selector` or `assertion`.
