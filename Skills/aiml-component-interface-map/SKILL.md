---
name: aiml-component-interface-map
description: "Statically build a substantially complete, source-backed interface and runtime-privilege baseline for a standalone third-party AI/ML component. Use when Codex must enumerate network/non-network interfaces, device/runtime/driver/IPC/fabric surfaces, workload-specific minimum-required versus default-requested privileges, listeners, security contracts, and operation planes from source and default configuration without probing deployments, analyzing platform integration, or producing vulnerability findings."
---

# AI/ML Component Interface Map

Build Stage A of the integration-security pipeline: **Know the Component**.

Scan only the third-party component and its own default configuration. Do not inspect or infer how
Kubeflow, KServe, Istio, a tenant gateway, or another integrating platform exposes or protects it.
Do not produce candidate vulnerabilities.

## Required references

Always read:

- [references/component-interface-workflow.md](references/component-interface-workflow.md) for the
  discovery process and completeness gate.
- [references/interface-schema.md](references/interface-schema.md) for the normative YAML contract.

Read [references/interface-discovery-adapters.md](references/interface-discovery-adapters.md) when
selecting search patterns for the component's frameworks. For mixed-language components, apply every
relevant adapter.

## Required workflow

```text
Component Fingerprint
  -> Listener Discovery
  -> Top-down Registration Walk
  -> Bottom-up Reverse Search
  -> Configuration-gated Discovery
  -> Cross-check and Deduplicate
  -> Interface Completeness Gate
  -> Component Interface Baseline
```

Treat a listener as any externally consumable registration root, including HTTP/gRPC/TCP servers,
WebSocket/SSE endpoints, Unix sockets, webhooks, Kubernetes CRDs/controllers, filesystem/object-store
contracts, database endpoints, library APIs, device nodes, shared-memory/IPC roots, OCI/CDI/runtime
hooks, driver/kernel interfaces, and RDMA/collective-fabric entrypoints exposed by the component.

Assign stable IDs:

```text
CLISTENER-{COMPONENT}-{NNN}
CIFACE-{COMPONENT}-{NNN}
CPRIV-{COMPONENT}-{NNN}
```

Preserve IDs across reruns when the same registration and operation still exist.

## Hard separation rule

The Stage A baseline may contain component defaults and component-authored security assumptions.
It must not contain platform observations or tenant exposure decisions. In particular, do not emit:

```yaml
observed_platform_protection:
observed_exposure:
ordinary_tenant_decision:
```

Record `unknown` with an evidence gap instead of filling missing component facts with platform
behavior.

Keep `minimum_required` distinct from `component_default_requested`. A shipped Helm chart or
manifest proves what the component requests by default, not what it minimally requires. Record
minimum necessity only from evidence and use `unknown` when it cannot be established.

## Outputs

Write:

```text
{report_dir}/stage-a-component-baseline/component-interface-map.md
{report_dir}/stage-a-component-baseline/interface-map.yaml
{report_dir}/stage-a-component-baseline/coverage-report.md
```

The Markdown map summarizes the component fingerprint, listeners, interface families, planes,
dangerous operations, workload privilege profiles, security contracts, and evidence. The YAML file follows the normative schema.
The coverage report records every completeness check, unmatched top-down/bottom-up result, excluded
surface, and remaining gap.

Default to Chinese prose unless the user requests another language. Keep identifiers and enum values
in English.

## Quality gate

Do not label the baseline `substantially_complete` unless:

- every discovered network listener and non-network registration root has been traced;
- routers/services and handlers/RPCs have been enumerated in both directions;
- dynamic/plugin registration, protobuf services, feature flags, and configuration-gated surfaces
  have been checked or explicitly marked not applicable;
- top-down and bottom-up inventories have been reconciled;
- excluded generated, test, deprecated, or client-only interfaces are listed with evidence;
- each interface has a listener/registration root, source evidence, plane, surface kind, security
  contract, and safe-probe decision.
- for accelerator-aware components, device/runtime/driver/IPC/fabric surfaces have been checked or
  explicitly marked not applicable.
- every component-defined default workload role and materially different supported profile has a
  `CPRIV-*` that distinguishes evidence-backed minimum requirements from component-default requests.

Otherwise set `coverage_status: incomplete` and state exactly what is missing. Completeness means
the method was exhausted with documented residual gaps; it never means mathematical proof.

## Safety

- Prefer source, specs, default configuration, and documentation.
- Do not send network requests, invoke reflection, inspect a live deployment, or perform metadata
  probes during this source-scan stage. The `automated_probe` field records whether a later,
  separately authorized validation workflow could safely probe an operation; it does not authorize
  this skill to execute the probe.
- Never submit jobs, execute code, mutate configuration or artifacts, invoke model lifecycle
  operations, or trigger controllers/webhooks with real objects during mapping.
- Mark dangerous operations `automated_probe: forbidden`; inventorying an operation is not invoking
  it.
