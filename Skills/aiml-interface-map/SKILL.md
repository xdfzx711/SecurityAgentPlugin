---
name: aiml-interface-map
description: "Map interfaces exposed by third-party AI/ML, MLOps, notebook, model-serving, telemetry, storage, runtime, dashboard, and management components after integration into GPU or AI compute platforms. Use when Codex needs to answer which interfaces exist, which interfaces are dangerous, which interfaces rely on external platform protection by default, and which interfaces should not be directly exposed to ordinary tenants, producing an interface map rather than a vulnerability report."
---

# AI/ML Interface Map

Use this skill to build an interface map for third-party AI/ML components integrated into a GPU or
AI compute platform.

The goal is not to produce a vulnerability report. The goal is to answer:

```text
Which interfaces exist?
Which interfaces are dangerous?
Which interfaces rely on external platform protection by default?
Which interfaces should not be directly exposed to ordinary tenants?
```

## Primary Reference

Always load [references/aiml-interface-map.md](references/aiml-interface-map.md) as the primary
workflow.

Use source review, OpenAPI/spec files, frontend routes, Kubernetes/Helm manifests, gateway/Ingress
rules, service definitions, component docs, and safe read-only probes as evidence.

Do not switch into candidate vulnerability reporting unless the user explicitly asks for a risk
report, PoC, CVE-style writeup, or manual verification plan. If a dangerous interface is found,
classify and map it; do not inflate it into a finding unless requested.

## Default Workflow

```text
Component Fingerprinting
  -> Interface Enumeration
  -> Protection Assumption Mapping
  -> Tenant Exposure Classification
  -> Dangerous Interface Marking
  -> Interface Map Rendering
```

1. Component Fingerprinting: identify third-party AI/ML components, versions, deployment mode,
   entrypoints, route prefixes, service names, and platform exposure paths.
2. Interface Enumeration: enumerate HTTP APIs, dashboards, WebSocket/SSE streams, gRPC services,
   notebook/runtime channels, model-serving endpoints, artifact/storage interfaces, telemetry,
   admin, and management surfaces.
3. Protection Assumption Mapping: mark whether each interface has built-in authn/authz, expects
   reverse-proxy or platform protection, is cluster-internal by design, or is unsafe without a
   platform control plane.
4. Tenant Exposure Classification: decide whether ordinary tenants, workspace users, service
   accounts, admins, anonymous callers, or only internal platform components should reach it.
5. Dangerous Interface Marking: mark state-changing, execution-capable, sensitive-read,
   management-plane, artifact-control, model-control, proxying, and cross-tenant visibility
   interfaces.
6. Interface Map Rendering: produce a concise map with tables and, when useful, Mermaid diagrams
   showing component-to-interface-to-protection-boundary relationships.

## Expected Outputs

Phase 1 must produce three user-facing files:

```text
{report_dir}/phase1-interface-map/{component_slug}_interface_map.md
{report_dir}/phase1-interface-map/external_protection_dependency_map.md
{report_dir}/phase1-interface-map/tenant_exposure_decision_map.md
```

Optional structured artifacts:

```text
{report_dir}/phase1-interface-map/raw/interface-map.yaml
{report_dir}/phase1-interface-map/raw/interface-map.mmd
```

For a Triton target, the first file must be named:

```text
{report_dir}/phase1-interface-map/triton_interface_map.md
```

The three files should be Chinese by default unless the user requests another language.

## Output Contract

The interface map must include:

- Component inventory.
- Component-specific interface enumeration tables, one component per file when the scope is narrow.
- Dangerous interface classification.
- External protection dependency mapping.
- Ordinary-tenant exposure decisions.
- Unknowns and evidence gaps.
- Safe next checks, limited to read-only or configuration review.

Use labels such as:

```text
safe_to_expose_to_tenant
tenant_exposure_requires_platform_authz
admin_or_platform_only
internal_only
destructive_do_not_call
unknown_needs_evidence
```

## Safety Rules

- Do not submit jobs, execute notebooks, invoke model loading, mutate registries, upload artifacts,
  delete resources, restart services, or send runtime-control payloads during mapping.
- Prefer static evidence and safe GET, HEAD, OPTIONS, OpenAPI, service discovery, and route
  extraction.
- For WebSocket/SSE/gRPC, record route, handshake, auth behavior, and intended consumer; do not
  send payloads that trigger execution or state changes.
- Mark risky interfaces as map entries, not confirmed vulnerabilities, unless the user asks for
  validation.
