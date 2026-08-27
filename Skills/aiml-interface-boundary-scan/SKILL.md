---
name: aiml-interface-boundary-scan
description: "Statically scan source code, manifests, policies, controllers, operators, SDKs, CRDs, and service contracts for security-boundary problems introduced when GPU platforms integrate third-party AI/ML components. Produce evidence-backed candidate issues and manual verification steps without executing PoCs, mutating resources, confirming vulnerabilities, or performing CVE triage."
---

# AI/ML Interface Boundary Source Scan

Discover security-boundary problems that may be introduced when a GPU platform integrates a third-party AI/ML component. Work from source code, default or recommended configuration, generated artifacts, and static service/policy contracts. Produce candidates for later human verification; do not perform that verification.

## Scope

Include direct and indirect integrations through:

- HTTP, gRPC, WebSocket, SSE, proxy, and library calls;
- workflow adapters, SDKs, CRDs, controllers, operators, webhooks, queues, and events;
- Kubernetes RBAC, ServiceAccounts, workload identity, IAM, and delegated roles;
- filesystems, object stores, databases, registries, artifacts, and generated resources;
- GPU devices, MIG/vGPU/time-slicing/MPS, IPC/shared memory, RDMA/fabrics, privileged GPU agents, runtimes, drivers, and kernel interfaces.

Ordinary injection, deserialization, path, authorization, or logic defects are in scope only when a real integration chain uses them to change a tenant, identity, authority, resource, accelerator, node, or control-plane boundary.

## Hard Phase Boundary

This skill performs source scanning only. It may write manual verification instructions, but it must not:

- submit workflows or jobs;
- send exploit requests or invoke state-changing operations;
- create, mutate, or delete Kubernetes or cloud resources;
- execute payloads, access real tenant data, or probe real GPU memory;
- mark a candidate `confirmed`, `exploitable`, `0-day`, or CVE-eligible;
- perform disclosure or CVE ownership triage.

Use only these final candidate states:

```text
source_supported_candidate
deployment_dependent_candidate
```

Keep unresolved ideas as internal `research_lead` records and excluded items as internal `rejected` records. Neither belongs in the final candidate report.

## Required Input

Collect or derive:

1. platform and component repository roots and frozen revisions;
2. integration source roots, including adapters, controllers, operators, SDKs, manifests, CRDs, and policies;
3. the matching Stage A `interface-map.yaml` from `aiml-component-interface-map`;
4. default and recommended deployment profiles relevant to the scan;
5. an explicit static threat model for tenant users, tenant workloads, service identities, node-local actors, and trust boundaries.

If Stage A is missing, create it with `aiml-component-interface-map` before candidate analysis. An incomplete Stage A does not globally block the scan: block or downgrade only candidates whose affected interface or privilege chain depends on the missing evidence.

## Required Workflow

Always read:

- [references/source-scan-workflow.md](references/source-scan-workflow.md) for the deterministic scan sequence and coverage gate;
- [references/boundary-model.md](references/boundary-model.md) for target, chain, evidence, and boundary semantics;
- [references/candidate-gate.md](references/candidate-gate.md) for candidate promotion, confidence, priority, and deduplication;
- [references/report-format.md](references/report-format.md) for the two final reports and mandatory manual-verification handoff.

Read [references/gpu-boundaries.md](references/gpu-boundaries.md) whenever the integration schedules accelerator workloads or deploys GPU operators, device plugins, runtimes, drivers, partitioning, MPS/IPC, or high-speed fabrics.

Execute the workflow in this order:

```text
Freeze Inputs and Revisions
  -> Define Threat Model
  -> Validate Stage A Handoff
  -> Inventory Integration Sources
  -> Discover Integration Entry Points
  -> Build Invocation / Identity / Parameter / Resource / Privilege Chains
  -> Locate and Evaluate Guards
  -> Compare Component Contract with Integrated State
  -> Apply Candidate Gate
  -> Deduplicate, Sort, Validate, and Report
```

Do not skip a step. Mark unavailable evidence `unknown` and record an evidence gap instead of inferring a safe or unsafe result.

## Concrete Targets

Use exactly these target kinds:

```text
component_interface          -> CIFACE-*  from Stage A
gpu_asset                    -> GASSET-*  from Stage B
platform_service_operation   -> PSOP-*    from Stage B
```

Never invent a `CIFACE-*` for a GPU asset or managed platform operation. Every candidate must terminate at one concrete target or concrete resource effect.

## Candidate Standard

Retain a candidate only when static evidence identifies:

1. a realistic low-privilege actor and controlled source;
2. a real integration path from that source to a concrete target;
3. the relevant authentication, authorization, validation, ownership, isolation, or policy guard;
4. a missing, mismatched, bypassed, overly broad, or deployment-dependent guard;
5. the security boundary that may be crossed;
6. a concrete confidentiality, integrity, availability, execution, tenant, GPU, node, or control-plane impact;
7. why integration introduces or enlarges the condition;
8. every runtime or deployment fact that remains for a human to verify.

A dangerous API, shared ServiceAccount, `iam:PassRole`, privileged workload, broad RBAC rule, GPU device, hostPath, or missing policy alone is an observation, not a candidate.

## Deterministic Artifacts

Write the internal machine-readable state to:

```text
{report_dir}/.scan-state/source-scan.json
```

It must conform to [references/source-scan.schema.json](references/source-scan.schema.json). Preserve stable IDs across reruns when the source, sink, boundary type, and affected integration path are unchanged. Validate it with:

```text
python scripts/validate_scan_output.py <source-scan.json>
```

## Final Outputs

Write exactly two human-readable Chinese Markdown reports:

```text
{report_dir}/component-boundary-scan.md
{report_dir}/candidate-vulnerabilities.md
```

Every final candidate must include vulnerability information, attacker capability, source evidence and integration chain, Root Cause, manual verification environment, numbered manual verification steps, positive and negative validation signals, possible impact, and safety restrictions.

Call severity `初步严重性`; it is a source-stage estimate. Do not calculate or claim CVSS unless a later human validation workflow explicitly requests it.

## Completion Gate

Finish only after:

- every applicable source role and path class is evaluated, `not_applicable` with evidence, or `unresolved` with a gap;
- every final candidate passes the candidate gate and has resolvable evidence and target IDs;
- every final candidate includes manual verification and falsification steps;
- unrelated coverage gaps do not silently suppress locally complete candidates;
- internal research leads and rejected items are absent from the final candidate report;
- the machine-readable state passes the bundled validator;
- both final reports follow the required Chinese format.
