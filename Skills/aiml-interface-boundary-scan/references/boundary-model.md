# Source Boundary Model

## Target kinds

Use one target kind and matching stable ID:

| Kind | ID | Meaning |
| --- | --- | --- |
| `component_interface` | `CIFACE-*` | Component operation from the Stage A baseline |
| `gpu_asset` | `GASSET-*` | Accelerator, IPC, runtime, fabric, driver, kernel, or privileged GPU asset |
| `platform_service_operation` | `PSOP-*` | Concrete platform or managed-service operation |

Do not use a component-interface ID for a platform API or GPU asset. Every referenced ID must resolve in the Stage A baseline or the internal source-scan document.

## Stable IDs

Use:

```text
ISRC-*    integration source
IBRIDGE-* integration bridge
PSOP-*    platform service operation
GASSET-*  GPU or node asset
CHAIN-*   invocation, parameter, identity, resource, or privilege chain
GUARD-*   security control
DELTA-*   security boundary delta
CAND-*    final candidate
LEAD-*    internal research lead
GAP-*     evidence or coverage gap
EVID-*    evidence object
```

Preserve an ID when its semantic source, target, boundary, and root-cause location remain the same. Renumbering because report order changed is forbidden.

## Evidence

Every security-relevant assertion cites an evidence object:

```yaml
evidence_id: EVID-001
evidence_type: source
source_id: ISRC-001
revision: <commit, version, digest, or contract date>
locator: <file, object, URL, or artifact>
selector: <line, symbol, YAML path, rule, or section>
assertion: <one fact supported by this evidence>
confidence: high
```

Allowed evidence types:

```text
source
default_config
recommended_config
generated_artifact
specification
service_contract
policy_contract
read_only_metadata
inference
```

Use `inference` only when it cites the underlying evidence IDs and states the reasoning. Static source scanning must not represent an unexecuted path as runtime observation.

## Chains

Each chain has one type:

```text
invocation
parameter
identity
resource_ownership
runtime_privilege
```

Each hop records participant, operation, input/output field or identity, transformation, guards, evidence, and status. Allowed statuses:

```text
resolved
partially_resolved
unresolved
```

A resolved chain has evidence for every critical source-to-target hop. A partially resolved chain can support a deployment-dependent candidate only when the missing fact is a runtime/deployment control with a precise manual verification condition. Missing source dispatch, target, actor control, or root-cause evidence keeps the item a research lead.

## Boundary dimensions

Classify every delta using one primary dimension:

```text
exposure
authentication
authorization
identity
parameter_authority
resource_ownership
caller_privilege
runtime_privilege
protocol_policy
configuration
storage
gpu_device
gpu_memory
gpu_partition
ipc_shared_memory
fabric
privileged_agent
driver_kernel
```

Additional dimensions may be tags. This dimension model is an analysis aid, not an eligibility whitelist: a new boundary pattern may become a candidate when it passes the same evidence gate.

## Threat origin

Keep these dimensions separate:

- actor class;
- network or resource origin;
- same-tenant versus another-tenant relation;
- initial platform-granted capabilities;
- effective credential at each hop.

Do not collapse a tenant user, code running in that user's workload, the workload ServiceAccount, a shared controller identity, and a cloud execution identity into one principal.

## Static reachability

Use:

```text
statically_proven
configuration_dependent
not_reachable
unresolved
```

`statically_proven` means the relevant source and default/recommended configuration establish all static edges; it does not mean runtime exploitability is confirmed. `configuration_dependent` requires an exact deployment condition and manual check. `unresolved` cannot enter the final candidate report.

## Guard semantics

Record authentication separately from authorization. Record the subject and resource actually evaluated. A UI check, shared network location, resource name, label, owner tag, or identity header is not an authorization boundary unless an evidence-backed enforcement point consumes it.

Gateway protection applies only to paths traversing that gateway. RBAC names do not prove effective permissions; resolve rules and bindings. A manifest request does not prove minimum necessity or final effective runtime privilege.
