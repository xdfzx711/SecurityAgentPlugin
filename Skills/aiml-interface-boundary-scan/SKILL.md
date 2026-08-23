---
name: aiml-interface-boundary-scan
description: "Analyze security deltas introduced when a platform integrates a third-party AI/ML component, including direct deployments and indirect workflow/controller/SDK/managed-service integrations. Resolve interface, platform-operation, GPU asset, identity, parameter, ownership, reachability/invocation, privilege, and policy boundaries from evidence-backed integration chains."
---

# AI/ML Interface Boundary Scan

Build Stages B–D of the integration-security pipeline:

```text
Know the Component -> Know the Integration -> Find the Security Delta -> Verify and Triage
```

This skill consumes a standalone Stage A component baseline. It does not rediscover component interfaces.

## Required inputs

Require:

1. `{report_dir}/stage-a-component-baseline/interface-map.yaml`;
2. evidence sufficient to fingerprint the declared platform/component pair and integration revision;
3. applicable integration evidence: source, adapters, controllers/operators, SDKs, CRDs, rendered manifests, RBAC, network/service-mesh policy, workload identity/IAM, service/API contracts, storage contracts, and safe read-only observations.

Do not require a monolithic open-source platform repository. A managed or partially closed platform may be analyzed from official API/service contracts, policy/IAM evidence, generated service models, adapter/controller source, deployment configuration, and read-only observations. Record unavailable implementation details as evidence gaps.

If Stage A is missing, stop candidate generation and create/request it with `aiml-component-interface-map`. If Stage A is incomplete or older than schema 3.0, propagate the gaps and keep affected interface/runtime-privilege conclusions scoped or unresolved.

## Required references

Always read:

- [references/platform-integration-workflow.md](references/platform-integration-workflow.md);
- [references/integration-topology-and-delegation.md](references/integration-topology-and-delegation.md);
- [references/integration-delta.md](references/integration-delta.md);
- [references/runtime-privilege-delta.md](references/runtime-privilege-delta.md);
- [references/aiml-risk-taxonomy.md](references/aiml-risk-taxonomy.md);
- [references/chinese-report-format.md](references/chinese-report-format.md).

`integration-topology-and-delegation.md` is normative for v6 indirect/delegated integrations and overrides any older assumption that a resolved integration must contain a direct source dependency, listener, proxy, or direct platform-to-component call.

`chinese-report-format.md` is normative for all human-readable Markdown reports. The Markdown output must use Chinese prose and the fixed candidate template defined there. Stable IDs, enum values, API/resource names, CWE/CVSS, source symbols, and necessary product names remain in their original form.

Read `cve-triage.md` for Stage D/ownership/disclosure decisions and `gpu-device-node-boundary.md` for accelerator-aware deployments.

## Workflow

```text
Platform / Component Fingerprint
  -> Integration Topology Resolver
  -> Integration Bridge Locator
  -> Interface / Platform-Operation Binding Resolver
  -> Parameter / Resource Propagation Mapper
  -> Reachability / Invocation Mapper
  -> Identity / Policy / Delegation Mapper
  -> Runtime / GPU Boundary Mapper
  -> Integration Delta Analyzer
  -> Candidate Generator
  -> Manual Verification and CVE Triage
```

Keep user-declared roles (`platform`, `component`) separate from observed roles such as `orchestrator`, `execution_backend`, `adapter`, and `controller`. The declared component may orchestrate work into the declared platform.

Resolve concrete targets as:

```text
CIFACE-*  Stage A component interface
GASSET-*  Stage B accelerator/node asset
PSOP-*    Stage B platform service operation
```

Never invent a `CIFACE-*` for a managed platform API, device, driver, kernel, or fabric target. A Service, CRD, SDK call, controller reconcile path, IAM policy, or resource reference proves only its own edge; build the full evidence chain.

For workflow/controller/SDK/managed-service integrations, explicitly trace both:

```text
user-controlled field -> adapter -> CRD/SDK/request -> controller/service operation -> authority/resource effect
```

and:

```text
user/tenant identity -> service account/workload identity -> controller identity -> cloud/service identity -> execution/resource identity
```

The absence of `kubeflow`, `sagemaker`, or another endpoint-specific keyword in one repository is not evidence that no integration exists when an adapter/controller/contract chain resolves the integration.

Treat arbitrary code inside an authorized tenant GPU workload as a baseline platform capability. Evaluate north-south, east-west, node-local, Kubernetes-control, non-network, controller-mediated, SDK-mediated, storage, and managed-service paths independently.

## Stage outputs

Write the existing Stage B–D artifacts plus, when applicable:

```text
{report_dir}/stage-b-platform-integration/parameter-propagation-map.md
{report_dir}/stage-b-platform-integration/resource-ownership-map.md
```

The normative Stage B YAML must include v6 topology/bridge/PSOP/parameter/identity/resource records defined in `integration-topology-and-delegation.md`.

### Human-readable report language

All human-readable Markdown reports under Stage A–D default to Chinese. YAML handoff schemas continue to use the existing English field names, IDs, and enum values so downstream automation remains stable.

The primary Stage C candidate report:

```text
{report_dir}/stage-c-security-delta/candidate-vulnerabilities.md
```

must follow `references/chinese-report-format.md` exactly. Every retained candidate uses a stable heading such as:

```markdown
### CAND-AIML-001: <中文候选漏洞标题>
```

and must contain, in order:

```text
组件
组件版本
Taxonomy
接口
协议/方法
漏洞类型
CWE
影响边界
严重性
评分
置信度
状态
验证优先级

预期边界
观察边界
当前证据
证据缺口
可能影响
误报条件
安全验证建议
禁止自动执行的危险步骤
修复建议
```

Do not omit empty sections. State `暂无已确认内容`, `待人工验证`, or another explicit unknown/gap marker instead of leaving sections blank.

Sort candidates by validation priority (`P0` -> `P1` -> `P2` -> `P3`), then by severity and confidence. Keep rejected/low-quality research leads separate from the main high-priority candidate list.

## Candidate gate

Do not retain a candidate merely because an interface, platform operation, GPU asset, shared identity, or sensitive parameter exists. Require an evidence-backed integration delta and answer the existing gate plus:

```yaml
integration_topology_resolved:
integration_bridge_resolved:
identity_chain_evaluated:
parameter_flow_evaluated:
resource_ownership_binding_evaluated:
```

At least one concrete target must exist: `CIFACE-*`, `GASSET-*`, or `PSOP-*`.

For indirect/delegated integrations, the relevant bridge, identity, parameter, and ownership chains must be resolved enough to state a concrete boundary and impact. Retain unresolved but plausible cases as `research_only`/`needs_evidence` rather than forcing them into candidate vulnerabilities.

## Taxonomy discipline

Use A1–A9 unchanged. Do not create A10 merely for cloud/controller/SDK integrations. Prefer:

- A1 for unauthorized backend management/lifecycle operations;
- A3 for delegated execution authority expansion;
- A4 for artifact/storage/resource-reference boundary drift;
- A7 for identity collapse, tenant/owner context loss, or cloud identity transition;
- A8 for CRD/API/controller/version/policy coverage mismatch;
- A9 only for accelerator/device/node isolation failures.

## Safety and claims

- Prefer static source/configuration/contracts and non-destructive metadata.
- Do not submit workflows, mutate CRDs/resources, create cloud resources, invoke state-changing service operations, read real tenant artifacts, execute payloads, or bypass live authorization.
- Every reachability/invocation edge, bridge hop, identity transformation, parameter flow, ownership binding, policy point, and delta must cite evidence; otherwise mark it unresolved.
- Do not mark Stage B complete for an indirect integration until topology, critical bridges, applicable identity chains, security-sensitive parameter flows, and ownership bindings are evaluated or evidence-backed `not_applicable`.
- Do not treat shared ServiceAccounts, IAM `PassRole`, privileged workloads, assigned GPU access, or dangerous operations alone as proof of a vulnerability.
- Call outputs candidates until authorized manual verification confirms the claim.
- Distinguish component behavior, adapter/controller behavior, platform/service root cause, deployment/policy misconfiguration, and shared ownership.
