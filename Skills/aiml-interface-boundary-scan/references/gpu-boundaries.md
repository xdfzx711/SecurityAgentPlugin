# GPU Source Boundary Checks

Load this reference only when accelerator workloads or GPU infrastructure are present.

## Threat boundary

Tenant-authorized code in its assigned GPU workload is the source trust domain. Ordinary assigned GPU access is not a vulnerability. Look for a statically supported path to another tenant, unassigned device or memory context, shared privileged service, node/kernel, control plane, or untrusted shared fabric.

## Mandatory coverage

Evaluate all eight rows:

```text
device_assignment
memory_lifecycle
partition_isolation
mps_and_ipc
shared_memory
rdma_and_collective_fabric
privileged_gpu_agents
driver_and_kernel
```

Each row is `evaluated`, evidence-backed `not_applicable`, or `unresolved`. Static evidence may create a candidate or research lead, never confirmation of dynamic isolation failure.

## Device assignment

Trace:

```text
resource request/limit
  -> scheduler/device plugin
  -> CDI/OCI/runtime injection
  -> device and control-device mounts
  -> device/runtime policy
  -> assigned GASSET-*
```

An environment variable, resource name, or device mount alone proves neither access nor isolation.

## Memory, partition, IPC, and shared memory

Record claimed and statically derived scope for memory reset/zeroization, MIG/vGPU/time-slicing/MPS isolation, MPS daemon identity and socket permissions, CUDA IPC, `hostIPC`, and `/dev/shm`. Device sharing alone does not prove cross-tenant leakage.

Memory-remanence verification instructions must require synthetic markers, two controlled workload lifecycles, and an authorized isolated node. Never read real tenant memory.

## RDMA and collective fabrics

Trace tenant workload access through RDMA device/VF, NetworkAttachment, host network, rendezvous membership, NCCL/collective configuration, and transport endpoint. Plaintext or unauthenticated transport alone is not a candidate; identify how an untrusted tenant could join, observe, inject, or interfere with the same domain.

## Privileged GPU agents

Inventory device plugins, GPU operators, runtime installers, driver managers, monitoring agents, Node Feature Discovery, and other node-wide workloads. Trace tenant-controlled CRDs, webhooks, sockets, metrics/control endpoints, writable files, parameters, or shared resources into their privileges.

Privilege alone is an observation. Require a tenant-controlled or tenant-reachable path and a concrete node, device, identity, or cluster boundary effect.

## Driver and kernel

Record versioned driver/kernel interfaces, device/control nodes, ioctl or library families, and the source/configuration path making them reachable. Device-node reachability is not proof of a driver vulnerability.

Manual instructions must prohibit ioctl fuzzing, module loading, device reset/crash, container escape attempts, real-memory reads, and joining real tenant collectives.

## Candidate subtypes

Use one primary subtype when the primary boundary is GPU-specific:

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

Each candidate identifies the source workload, target `GASSET-*`, expected isolation, statically derived enforcement, unresolved deployment checks, and plausible impact scope.
