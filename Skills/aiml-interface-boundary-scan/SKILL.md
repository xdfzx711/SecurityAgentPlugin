---
name: aiml-interface-boundary-scan
description: "Analyze security deltas introduced when a platform integrates a third-party AI/ML component. Use with a Stage A interface/runtime-privilege baseline plus platform source and deployment configuration to resolve component/GPU-asset bindings, workload and node reachability, caller identity, component runtime over-privilege, device/driver/partition/memory/IPC/fabric risks, candidate vulnerabilities, verification, ownership, and CVE triage."
---

# AI/ML Interface Boundary Scan

Build Stages B–D of the integration-security pipeline:

```text
Know the Component -> Know the Integration -> Find the Security Delta -> Verify and Triage
```

This skill consumes a standalone component baseline. It does not rediscover the component's
interface inventory.

## Required inputs

Require:

1. `{report_dir}/stage-a-component-baseline/interface-map.yaml`;
2. platform source at a known revision;
3. platform deployment evidence such as Helm values, rendered YAML, operators, gateways, service
   mesh policies, RBAC, network policy, workload pod specifications, node-local mounts/endpoints,
   device access, and workload identity configuration.

If the Stage A baseline is missing, stop candidate generation and request or create it with
`aiml-component-interface-map`. If its `coverage_status` is `incomplete`, continue only as a scoped
analysis and propagate the gaps to every affected binding and candidate. Never silently compensate
by rescanning component source.

Stage A schema 3.0 is required for complete runtime-privilege analysis. Treat older baselines as
scoped inputs and keep affected `CPRIV-*`/`RPBIND-*` mappings and candidates unresolved until a
matching baseline is produced.

## Required references

Always read:

- [references/platform-integration-workflow.md](references/platform-integration-workflow.md);
- [references/integration-delta.md](references/integration-delta.md);
- [references/runtime-privilege-delta.md](references/runtime-privilege-delta.md);
- [references/aiml-risk-taxonomy.md](references/aiml-risk-taxonomy.md).

Read [references/cve-triage.md](references/cve-triage.md) when producing Stage D, disclosure
priorities, CVE likelihood, or ownership decisions.

Read [references/gpu-device-node-boundary.md](references/gpu-device-node-boundary.md) whenever the
platform schedules accelerator workloads or deploys accelerator operators, device plugins,
runtimes, drivers, partitioning, shared execution services, or high-speed training fabrics.

## Workflow

```text
Platform Fingerprint
  -> Integration Component Locator
  -> Interface Binding Resolver
  -> Reachability Mapper
  -> Identity / Policy Mapper
  -> Integration Delta Analyzer
  -> Candidate Generator
  -> Manual Verification and CVE Triage
```

The resolver must map component operations to existing `CIFACE-*` IDs and platform accelerator/node
targets to evidence-backed `GASSET-*` IDs. Never invent a component interface for a device, memory
context, driver, kernel module, fabric, or privileged node agent. A Service, Ingress, open port, or
device mount proves only its own edge; build the full evidence chain to the concrete target.

Treat arbitrary code execution inside a tenant GPU workload as a normal platform-granted starting
capability, not as a prior compromise or an impact. Always evaluate applicable workload-origin,
cross-tenant, node-local, Kubernetes-control, and non-network paths independently of north-south
Ingress/Gateway paths. An authenticated platform facade does not protect a direct ClusterIP, Pod IP,
Unix socket, device file, mounted credential, kubelet, or metadata-service path unless evidence shows
that the same control applies there.

## Stage outputs

Write:

```text
{report_dir}/stage-b-platform-integration/interface-binding-map.md
{report_dir}/stage-b-platform-integration/reachability-map.md
{report_dir}/stage-b-platform-integration/identity-policy-map.md
{report_dir}/stage-b-platform-integration/runtime-privilege-map.md
{report_dir}/stage-b-platform-integration/gpu-device-node-boundary-map.md
{report_dir}/stage-b-platform-integration/platform-integration.yaml

{report_dir}/stage-c-security-delta/integration-delta.md
{report_dir}/stage-c-security-delta/candidate-vulnerabilities.md
{report_dir}/stage-c-security-delta/security-delta.yaml

{report_dir}/stage-d-verification/verification-plan.md
{report_dir}/stage-d-verification/cve-triage.md
{report_dir}/stage-d-verification/verification-triage.yaml
```

The YAML handoff artifacts are required. Use the exact document schemas in the references. Default
to Chinese prose and English identifiers/enums.

## Candidate gate

Do not retain a candidate merely because a component interface or GPU/node asset is dangerous. Require an
evidence-backed integration delta and answer:

```yaml
integration_induced:
present_in_standalone_equally:
default_or_recommended_integration:
requires_explicit_insecure_config:
low_privilege_reachable:
tenant_workload_origin_evaluated:
gpu_boundary_coverage_complete:
runtime_privilege_profiles_mapped:
runtime_privilege_expanded:
security_boundary_crossed:
documented_behavior:
supported_version_affected:
root_cause_owner:
```

Prioritize candidates where integration induced or materially amplified the behavior, a security
boundary was crossed, no explicit insecure configuration was required, and a supported version is
affected. Retain weaker cases as `research_only` or reject them with the reason.

## Taxonomy discipline

Use A1–A9 unchanged as the candidate taxonomy. A9 is reserved for accelerator device, memory,
partition, IPC, fabric, privileged node-agent, driver, and kernel isolation boundary failures. Do
not create a new category just to describe a new surface. `Orchestration / Kubernetes Control` is an
interface family and `surface_kind` is evidence, not a new risk taxonomy.

## Safety and claims

- Prefer static platform source/configuration and non-destructive route metadata.
- Do not submit workflows, invoke model loading/reload, mutate CRDs, read real tenant artifacts,
  execute code, or bypass live authorization.
- Every reachability edge, identity transformation, policy point, and delta must cite source or
  configuration evidence; otherwise mark it unresolved.
- Do not mark Stage B complete until every applicable tenant-workload and node-local origin is
  evaluated or has evidence-backed `not_applicable` status.
- For GPU-enabled deployments, do not mark Stage B complete until all required GPU boundary coverage
  rows are evaluated or have evidence-backed `not_applicable` status.
- Do not treat assigned GPU access, a privileged system DaemonSet, a sharing mode name, plaintext
  collective transport, or driver reachability alone as proof of a vulnerability.
- Do not treat a component's default privilege request as its minimum requirement, or runtime
  over-privilege alone as proof of exploitability.
- Call outputs candidates until safe manual verification confirms the claim.
- Distinguish component behavior, platform root cause, deployment misconfiguration, and shared
  ownership.
