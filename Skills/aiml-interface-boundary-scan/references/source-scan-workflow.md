# Deterministic Source Scan Workflow

## Purpose

Run the same ordered static-analysis procedure for every platform/component pair. Deterministic means frozen inputs, mandatory coverage rows, stable identifiers, explicit gates, and schema validation. It does not imply that semantic source analysis is mathematically complete.

## 0. Freeze inputs

Record the repository or artifact, revision, and scanned root for every available source role:

```text
platform
component
integration_adapter
controller
operator
sdk
deployment
service_contract
policy_contract
storage_contract
generated_artifact
```

Do not merge assertions from incompatible revisions. Classify configuration provenance as:

```text
source_default
packaging_default
recommended_example
generated_default
test_or_example_only
user_override
unknown
```

Only the first four can support a default/recommended integration claim. A site-specific override can support a deployment-dependent candidate but not a default-integration claim.

## 1. Define the threat model

Record each applicable actor independently:

- ordinary tenant user;
- same-tenant workload process;
- another-tenant workload process;
- workload or controller ServiceAccount;
- node-local process;
- platform administrator.

For every actor record origin, tenant relationship, initial platform-granted capabilities, credentials, network/resource reach, and excluded higher privileges. Treat arbitrary code inside an authorized tenant GPU workload as a normal starting capability when the platform offers such workloads. Do not describe it as a prior compromise.

## 2. Validate the Stage A handoff

Load the component baseline and verify its schema version, component revision, IDs, coverage, residual gaps, security contracts, and runtime privilege profiles.

Classify compatibility:

- `exact`: source commit or image digest matches;
- `verified_equivalent`: reproducible evidence establishes equivalent code and interface-affecting configuration;
- `incompatible`: an identified difference can change the affected interface or privilege contract;
- `unknown`: equivalence cannot be established.

Compatibility is evaluated per affected interface or privilege chain. An unrelated Stage A gap must not block a locally complete candidate. An incompatible or unknown affected chain becomes a research lead until a matching baseline exists.

## 3. Inventory integration sources

Create one source record for every relevant repository root, manifest set, CRD, generated object, SDK model, policy, and service contract. Record missing expected source roles as gaps.

Run repository-wide discovery before following individual matches. Use `rg --files` first, then search all applicable categories:

| Category | Required source seeds |
| --- | --- |
| Network/API | route registration, listeners, protobuf services, gateway/proxy rules, methods, rewrites, WebSocket/SSE upgrades |
| Kubernetes | CRDs, reconcilers, watches, webhooks, ServiceAccounts, Roles, ClusterRoles, bindings, admission mutation |
| Workflows/SDK | component inputs, client calls, request models, job/resource creation, queues, callbacks |
| Identity | tokens, identity headers, workload identity, role assumption, `PassRole`, impersonation |
| Resources | names, owner references, tags, namespaces, projects, accounts, buckets, prefixes, ARNs, adoption/reference paths |
| Runtime | Pod templates, securityContext, host namespaces, hostPath, capabilities, automount tokens, RuntimeClass |
| GPU/node | device resources and nodes, CDI/OCI injection, MPS/IPC, shared memory, RDMA, fabrics, privileged agents, drivers |

Search seeds are discovery aids, not proof. Trace each retained match through registration, dispatch, transformation, authorization, and effect.

## 4. Discover entry points and targets

Evaluate every path class:

```text
north_south
workload_east_west
node_local
kubernetes_control
non_network
storage
controller_or_sdk
managed_service
```

For each class record `evaluated`, evidence-backed `not_applicable`, or `unresolved`. Identify concrete targets as `CIFACE-*`, `GASSET-*`, or `PSOP-*`.

A Service, route, CRD, SDK call, device mount, or policy proves only its own edge. Do not infer an entire path from one object. Do not infer safety for direct-cluster, node-local, storage, or non-network paths from an authenticated north-south path.

## 5. Build ordered chains

Create all applicable chains:

```text
Invocation:
actor -> entry -> bridge/dispatcher -> guard -> target

Parameter:
controlled field -> transformations -> validation -> authorization -> sink effect

Identity:
user/workload -> service account -> controller -> cloud/runtime identity -> execution/resource identity

Resource ownership:
source owner/object -> intermediate object -> target resource -> read/update/delete/reference/adopt authority

Runtime privilege:
Stage A minimum/default -> platform template -> operator/admission/runtime injection -> effective static grant
```

Every critical hop needs evidence. Dynamic dispatch or generated behavior that cannot be resolved produces a gap; it must not be silently treated as reachable or protected.

Prioritize parameters selecting identities, executable images, commands, models, artifacts, paths, storage locations, encryption keys, networks, resource names, accounts, regions, device profiles, and owner metadata.

## 6. Locate and evaluate guards

For every source-to-target chain identify each expected guard:

- authentication and credential integrity;
- object, tenant, namespace, workspace, project, role, and owner authorization;
- parameter validation, canonicalization, allowlists, and immutable fields;
- route, method, protocol, version, and subresource coverage;
- RBAC, IAM, role delegation, and ServiceAccount scope;
- resource ownership binding and cross-tenant reference checks;
- network, filesystem, storage, device, runtime, IPC, fabric, driver, and node isolation.

Record the subject evaluated, resource evaluated, decision scope, default action, rule precedence, and source evidence. Classify the result:

```text
present_and_bound
missing
misbound
partial
bypass_path
deployment_dependent
unknown
```

An absence claim must state the searched registration stacks, middleware, policies, and reverse-search scope. Keyword absence alone is not evidence that a guard or integration is absent.

## 7. Compute boundary deltas

Compare the component-native or platform-declared contract with the statically derived integration state for:

- exposure and caller class;
- authentication and authorization;
- identity preservation, collapse, reconstruction, and amplification;
- parameter authority and validation;
- resource ownership and reference scope;
- caller and component runtime privilege;
- configuration and protocol coverage;
- storage and artifact scope;
- GPU assignment, memory lifecycle, partition, IPC, shared memory, fabric, privileged agent, driver, and kernel boundaries.

Record the expected boundary, observed static state, changed dimension, comparison basis, evidence, and unresolved deployment conditions. A dangerous operation or privileged asset without a changed boundary is not a delta.

## 8. Apply the candidate gate

Apply [candidate-gate.md](candidate-gate.md). Locally complete evidence can support a candidate even when unrelated scan coverage is incomplete. Any unresolved critical hop in the affected chain remains a research lead.

## 9. Deduplicate, sort, and validate

Derive stable candidate identity from:

```text
platform + component + actor/source + target + boundary type + root-cause location
```

Merge protocol/path variants only when they share the same guard, target, root cause, deployment conditions, and impact. Otherwise keep separate candidates.

Sort by manual verification priority, preliminary severity, confidence, then candidate ID. Write the internal JSON and two reports. Run the bundled validator before completion.

## Coverage gate

The internal state must contain one coverage row for every source role and path class expected by the schema. `not_applicable` requires evidence. `unresolved` requires a stable gap ID and affected scope.

Maintain two separate conclusions:

- `scan_coverage`: overall repository and configuration coverage;
- `candidate_chain_complete`: whether one candidate's affected chain is locally complete.

Never use an unrelated coverage gap to hide a complete candidate, and never use high overall coverage to promote an unresolved candidate chain.
