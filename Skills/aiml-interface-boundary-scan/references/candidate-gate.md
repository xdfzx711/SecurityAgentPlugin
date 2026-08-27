# Source Candidate Gate

## Promotion requirements

Promote an item to a final candidate only when all are true:

1. **Actor**: a realistic low-privilege actor and initial capability are explicit.
2. **Controlled source**: the actor controls a concrete request field, object, resource, identity, path, workload input, or reachable entrypoint.
3. **Integration chain**: source, bridge/dispatcher, guard, and target are evidence-backed.
4. **Concrete target**: the chain terminates at a `CIFACE-*`, `GASSET-*`, `PSOP-*`, or specifically named resource effect.
5. **Boundary delta**: expected and statically derived boundaries differ in a security-relevant way.
6. **Root cause**: the missing, misbound, partial, bypassed, overly broad, or deployment-dependent control is located in source, policy, configuration, or a contract.
7. **Integration relevance**: integration creates or enlarges the path, authority, resource scope, identity transition, or impact.
8. **Impact**: confidentiality, integrity, availability, execution, cross-tenant, GPU, node, or control-plane impact is concrete.
9. **Manual handoff**: deployment conditions, verification steps, positive signals, negative signals, evidence to collect, and prohibited actions are present.

The existence of a dangerous operation, shared identity, broad role, privileged workload, GPU asset, host mount, or missing policy is insufficient by itself.

## Final status

Use `source_supported_candidate` when:

- every critical source hop is resolved;
- the relevant condition exists in source-default, packaging-default, generated-default, or recommended configuration;
- the source evidence identifies the changed boundary and plausible impact.

Use `deployment_dependent_candidate` when:

- the source chain and root cause are resolved;
- one or more runtime facts such as effective RBAC, IAM, network reachability, admission mutation, RuntimeClass/CDI injection, device enforcement, or tenant placement decide exploitability;
- each unknown is expressed as a precise manual verification condition.

Use internal `research_lead` when the actor-controlled source, critical dispatch, target, guard, boundary delta, or root cause is unresolved. Use internal `rejected` when evidence proves the chain unreachable, guarded, standalone-equivalent without integration expansion, test-only, incompatible, or dependent solely on an explicit unsupported insecure modification.

## Confidence

- `high`: source, configuration, guard, target, and boundary comparison are direct and revision-matched.
- `medium`: the chain is resolved but one comparison relies on a labeled inference or deployment-dependent control.
- `low`: do not publish as a final candidate; retain as a research lead.

## Preliminary severity

Severity is a source-stage estimate, not CVSS:

- `Critical`: plausible unauthenticated or ordinary-tenant path to cross-tenant execution, control-plane/node/kernel compromise, or broad secret/data compromise.
- `High`: plausible cross-tenant access, privileged operation, shared GPU data exposure, or substantial resource integrity impact.
- `Medium`: bounded disclosure or integrity impact requiring meaningful deployment conditions.
- `Low`: normally retain as an observation or research lead unless the boundary impact is concrete.

## Manual verification priority

- `P0`: plausible node/kernel/control-plane crossing, cross-tenant GPU data exposure, shared-fabric compromise, or broad delegated execution.
- `P1`: concrete cross-tenant or management/resource-control boundary.
- `P2`: bounded issue or material deployment-dependent candidate.
- `P3`: lower-impact candidate with complete evidence.

Priority orders human work; it does not confirm validity or severity.

## False-positive discipline

Every candidate must state conditions that would disprove or downgrade it, including applicable backend authorization, identity preservation, object ownership enforcement, network isolation, effective RBAC/IAM restriction, device assignment enforcement, feature disablement, or incompatible deployment profiles.

Do not reject a condition merely because an authenticated Ingress exists when the relevant path is direct-cluster, node-local, controller-mediated, storage, or non-network. Do not promote a condition merely because a guard was not found by keyword search.

## Deduplication

Merge findings only when actor, controlled source, target, root cause, guard coverage, deployment conditions, and impact are materially identical. Keep REST/gRPC, versioned API, direct/proxy, same-tenant/cross-tenant, and network/non-network variants separate when policies or impacts differ.

Assign one primary boundary dimension and optional secondary tags. Taxonomy tags organize findings but never replace the evidence gate.
