# Runtime Privilege Contract and Delta

Apply this reference to every deployed component workload role. Keep caller authority separate from
the privileges granted to the component process itself.

## Three-state comparison

Compare three distinct states:

```text
Stage A minimum_required
        vs
Stage A component_default_requested
        vs
Stage B platform_effective_granted
```

A component manifest proves a default request, not minimum necessity. Platform source values prove
an input, not necessarily the effective workload after operator rendering, admission mutation,
RuntimeClass, CDI/device-plugin injection, and RBAC resolution.

## Stage B runtime privilege binding

Create one binding per deployed component workload and Stage A `CPRIV-*` profile:

```yaml
runtime_privilege_binding_id: RPBIND-NVIDIA-001
component_privilege_profile_id: CPRIV-NVIDIA-001
integration_workload:
  kind: <Deployment | StatefulSet | DaemonSet | Pod | Job | other>
  namespace: <namespace>
  name: <name>
  workload_role: <controller | daemon | server | worker | webhook | installer | exporter | other>
effective_privileges:
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
      purpose: <reason | unknown>
  device_access:
    - locator: <device path or accelerator resource>
      permissions: <read | write | rw | mknod | rwm | unknown>
      scope: <assigned_device | all_devices | control_device | unknown>
      injection_source: <pod_spec | device_plugin | CDI | runtime | other | unknown>
  service_account: <name | not_applicable | unknown>
  automount_service_account_token: <true | false | unknown>
  resolved_service_account_permissions:
    - api_groups: []
      resources: []
      verbs: []
      resource_names: []
      non_resource_urls: []
      scope: <namespace | cluster | unknown>
  runtime_class: <name | not_applicable | unknown>
  runtime_controls:
    seccomp: <profile | absent | unknown>
    apparmor: <profile | absent | unknown>
    selinux: <type | absent | unknown>
    read_only_root_filesystem: <true | false | unknown>
derivation:
  rendered_workload_evidence: []
  operator_generated_evidence: []
  admission_mutation_evidence: []
  runtime_or_cdi_injection_evidence: []
  resolved_rbac_evidence: []
evidence_gaps: []
status: <resolved | partially_resolved | unresolved>
```

Do not mark a binding `resolved` from Helm values alone when an operator, admission controller,
security policy, runtime, CDI, or device plugin can change the effective result.

## Stage C runtime privilege delta

Rename the existing caller comparison to `caller_privilege_delta`. Add:

```yaml
runtime_privilege_delta:
  component_privilege_profile_id: CPRIV-NVIDIA-001
  runtime_privilege_binding_id: RPBIND-NVIDIA-001
  before:
    minimum_required: <structured Stage A privilege set>
    component_default_requested: <structured Stage A privilege set>
  after:
    platform_effective_granted: <structured Stage B privilege set>
  expansion:
    privileged_added: <true | false | unknown>
    allow_privilege_escalation_added: <true | false | unknown>
    root_execution_added: <true | false | unknown>
    added_capabilities: []
    added_host_namespaces: []
    added_host_mounts: []
    broadened_host_mounts: []
    added_device_access: []
    broadened_device_scope: []
    service_account_token_added: <true | false | unknown>
    added_service_account_permissions: []
    rbac_scope_expansion: []
    weakened_runtime_controls: []
  comparison:
    exceeds_minimum_required: <true | false | unknown>
    exceeds_component_default: <true | false | unknown>
    required_features_enabled: []
    excess_privileges_justified: <true | false | unknown>
  changed: <true | false | unknown>
  material_security_expansion: <true | false | unknown>
  evidence: []
  evidence_gaps: []
```

Use literal `not_applicable` only when the delta record cannot concern a deployed component
workload. Otherwise unresolved before/after evidence produces `unknown`, not `not_applicable`.

## Normalization and comparison

Compare semantic privilege sets, not YAML text:

- host mount: adding a mount, read-only -> read-write, child -> parent path, or weaker mount
  propagation is an expansion;
- device: assigned -> all/control devices, narrower -> broader path/resource set, or read -> rw/rwm
  is an expansion;
- capabilities: compare effective added/dropped sets after privileged-mode semantics;
- namespaces: false -> true for host PID/IPC/network is an expansion;
- identity: non-root -> root and denied -> allowed privilege escalation are expansions;
- workload identity: absent -> automounted ServiceAccount token is an expansion;
- RBAC: compare API groups/resources/verbs/resourceNames/non-resource scope after RoleBinding and
  ClusterRoleBinding resolution; wildcard, namespace -> cluster, secret/node/pods-exec, `bind`,
  `escalate`, or `impersonate` expansion must remain visible;
- runtime controls: loss or weakening of seccomp, AppArmor, SELinux, or read-only-root-filesystem is
  an expansion.

Record missing required privileges separately as an operational/availability mismatch; do not
mislabel them as security over-privilege.

## Candidate and ownership gate

Runtime over-privilege alone is an attack-surface observation. Generate a vulnerability candidate
only when evidence also establishes a tenant-reachable or tenant-controlled path, a concrete
boundary expansion, default/recommended integration relevance, and plausible security impact.

Assign ownership using both Stage A states:

- platform: effective grant exceeds both minimum and component default;
- component: component default exceeds its evidence-backed minimum and platform does not amplify it;
- both: component over-requests and platform integration adds reachability, authority, or further
  expansion necessary for impact;
- deployment: only a site-specific override creates the expansion;
- unknown: minimum requirement or effective grant cannot be resolved.

Use A9 `privileged_gpu_agent_exposure` for accelerator/node agents, A3 for generic runtime execution
authority drift, A6 as default-deployment evidence, and A7 when the material expansion is workload
identity or ServiceAccount authorization. Keep one primary taxonomy per candidate.

## Safe verification

Prefer manifest/operator rendering, admission-policy evaluation, effective PodSpec inspection,
RuntimeClass/CDI/device mapping, and static RBAC resolution. Do not mount host paths, read host files,
invoke privileged operations, escape containers, mutate RBAC, or use real tenant workloads during
verification.
