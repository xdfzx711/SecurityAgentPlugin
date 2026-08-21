# GPU Device and Node Boundary Workflow

Apply this reference whenever the integrated platform schedules accelerator workloads or deploys
GPU/accelerator operators, device plugins, runtimes, drivers, partitioning, shared execution
services, or high-speed training fabrics.

## Security boundary

Tenant-authorized code inside a GPU workload is the source trust domain. Inventory the mechanisms
that are expected to confine it to its assigned accelerator, memory, IPC, fabric, and node scope.
Do not treat ordinary GPU access as a vulnerability. Generate an A9 candidate only when integration
evidence shows or plausibly shows expansion to another tenant, an unassigned device or memory
context, a shared privileged service, the node kernel, the control plane, or a cross-tenant fabric.

## GPU asset inventory

Create a stable Stage B asset record for every security-relevant accelerator or node target that is
not a Stage A component interface:

```yaml
asset_id: GASSET-NVIDIA-001
kind: <physical_gpu | mig_instance | vgpu | gpu_memory_context | device_node |
       mps_daemon | ipc_namespace | shared_memory | rdma_device | collective_fabric |
       container_runtime | gpu_driver | kernel_module | privileged_daemonset | other>
vendor: <NVIDIA | AMD | Intel | other | unknown>
locator: <resource name/device path/socket/DaemonSet/module/fabric/config reference>
node_scope: <node | node_pool | cluster | external_fabric | unknown>
tenant_sharing: <exclusive | partitioned | time_shared | shared_service | unknown>
allocation_mode: <full_gpu | MIG | vGPU | time_slicing | MPS | mixed | not_applicable | unknown>
security_role: <assigned_data_device | control_device | memory_context | isolation_mechanism |
                privileged_broker | transport | kernel_boundary | other>
evidence: []
evidence_gaps: []
```

`GASSET-*` identifies an observed platform/node asset; it is not a substitute for a missing
component `CIFACE-*`. A component operation still uses its Stage A ID. A reachability path may target
either kind.

## Required coverage

Create one coverage record for every boundary below:

```yaml
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
```

For a GPU-enabled deployment, Stage B cannot be `complete` until all eight rows exist. An omitted
row is unresolved. `not_applicable` requires deployment evidence.

## Device assignment

Resolve the full effective assignment chain:

```text
Pod resource request/limit
 -> scheduler and device-plugin allocation
 -> CDI/OCI/runtime injection
 -> environment variables
 -> actual device and control-device mounts
 -> device-cgroup/runtime enforcement
 -> assigned GPU asset
```

Inspect rendered workloads, `NVIDIA_VISIBLE_DEVICES`, vendor resource names, MIG resource names,
RuntimeClass, CDI specifications, containerd/CRI-O and accelerator-runtime configuration,
`privileged`, capabilities, host namespaces, device mounts, seccomp, AppArmor/SELinux, and effective
device rules. An environment variable alone proves neither access nor isolation. Ordinary access to
an assigned data device is not a candidate; require over-broad assignment, an unassigned/control
device, missing enforcement, or a larger privilege boundary.

## Memory lifecycle

Record:

```yaml
memory_lifecycle:
  reuse_scope: <same_process | same_workload | same_tenant | cross_tenant | unknown>
  reset_between_allocations: <true | false | unknown>
  zeroization_guarantee: <documented | observed | absent | unknown>
  reset_owner: <driver | runtime | scheduler | platform | unknown>
  evidence: []
```

Static evidence normally produces a candidate or research lead, not confirmation of residual-memory
disclosure. Do not infer leakage from device sharing alone. Any dynamic confirmation must use an
authorized isolated node, synthetic marker data, two controlled workload lifecycles, and no real
tenant memory.

## Partitioning and multiplexing

For full GPU, MIG, vGPU, time-slicing, MPS, or mixed modes, record each isolation dimension:

```yaml
partition_isolation:
  mode: <full_gpu | MIG | vGPU | time_slicing | MPS | mixed | unknown>
  memory: <isolated | shared | unknown>
  compute: <isolated | shared | unknown>
  control_interface: <isolated | shared | unknown>
  fault_domain: <isolated | shared | unknown>
  telemetry: <isolated | shared | unknown>
  expected_tenant_boundary: <exclusive | same_tenant_shared | cross_tenant_allowed | unknown>
  evidence: []
```

Do not treat a mode name as proof of a security guarantee. Compare the platform's claimed tenant
boundary with the concrete profile, device allocation, shared services, and vendor/runtime contract.

## MPS, IPC, and shared memory

Inspect MPS daemon identity, control/socket directories, file ownership and permissions, tenant
sharing, lifecycle, and whether client input reaches a more privileged daemon. Separately inspect
`hostIPC`, pod/container IPC mode, CUDA IPC handle exchange, `/dev/shm` type and mount source,
hostPath-backed shared memory, and sharing across pods or tenants. Shared IPC is a candidate only
when it crosses the intended workload/tenant boundary or grants access to a more privileged service.

## RDMA, InfiniBand, NCCL, and GPUDirect

Trace:

```text
Tenant GPU Pod
 -> RDMA device / SR-IOV VF / NetworkAttachment / host network
 -> InfiniBand or RoCE fabric / collective rendezvous
 -> peer workload or privileged transport endpoint
```

Inspect `/dev/infiniband/*`, RDMA device plugins, NetworkAttachmentDefinitions, SR-IOV allocation,
`IPC_LOCK`, host networking, NCCL configuration and bootstrap/rendezvous credentials, GPUDirect
components, peer membership, and network/fabric segmentation. Plaintext or unauthenticated
collective transport is not by itself a candidate; prove that an untrusted tenant can observe,
inject, join, or interfere with the same communication domain.

## Privileged GPU infrastructure

Inventory GPU Operator, device plugin, Node Feature Discovery, monitoring agents, runtime installers,
driver managers, and similar node-wide workloads. Record privileged mode, host namespaces, hostPath
and device mounts, capabilities, ServiceAccount/RBAC, writable inputs, CRDs/webhooks, sockets, and
tenant-reachable interfaces. Privilege alone is an attack-surface observation. Generate a candidate
only when a tenant-controlled path, integration-induced over-privilege, unsafe mutable input, or
supported affected version makes the node boundary plausibly crossable.

For every such workload, resolve the Stage A `CPRIV-*` minimum/default contract to the Stage B
`RPBIND-*` effective grant using [runtime-privilege-delta.md](runtime-privilege-delta.md). Compare
hostPath access/propagation, devices, capabilities, host namespaces, runtime controls, and resolved
ServiceAccount rules; do not infer necessity from privileged component manifests.

## Driver and kernel boundary

Record accelerator driver and kernel-module versions, exposed device/control nodes, reachable
ioctl/library families, runtime and device restrictions, and supported-version vulnerability
evidence. Device-node reachability is not proof of a driver vulnerability or container escape.
Ordinary integration scanning must not fuzz ioctls, load kernel modules, crash/reset devices, or run
escape probes. Keep unsupported exploitability claims as research leads.

## A9 candidate contract

Every A9 candidate includes:

```yaml
a9_subtype: <device_assignment_exposure | gpu_memory_remanence |
             partition_isolation_failure | shared_mps_ipc | shared_memory_ipc |
             fabric_transport_boundary | privileged_gpu_agent_exposure |
             driver_kernel_boundary>
source_workload: <tenant workload identity/reference>
target_asset_id: GASSET-NVIDIA-001
expected_isolation: <structured platform/component/vendor contract>
observed_enforcement: <structured evidence-backed state>
impact_scope: <another_tenant | shared_gpu | node | cluster | fabric | unknown>
critical_boundary:
  node_or_kernel_crossed: <true | false | unknown>
  cross_tenant_gpu_data_exposed: <true | false | unknown>
  shared_fabric_compromised: <true | false | unknown>
false_positive_conditions: []
safe_verification_steps: []
prohibited_actions: []
```

Place evidence-backed default-integration candidates in the first manual-review queue when a
low-privilege tenant workload plausibly crosses the node/kernel boundary, exposes cross-tenant GPU
data, or compromises a shared fabric. This is scan/verification ordering, not an unconditional
severity or CVE conclusion.
