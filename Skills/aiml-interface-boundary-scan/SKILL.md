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

`integration-topology-and-delegation.md` is normative for v6 indirect/delegated integrations and overrides older assumptions that a resolved integration must contain a direct source dependency, listener, proxy, or direct platform-to-component call.

`chinese-report-format.md` is normative for final output formatting.

Read `cve-triage.md` for Stage D/ownership/disclosure decisions and `gpu-device-node-boundary.md` for accelerator-aware deployments when applicable.

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

The absence of endpoint-specific keywords in one repository is not evidence that no integration exists when an adapter/controller/contract chain resolves the integration.

Treat arbitrary code inside an authorized tenant GPU workload as a baseline platform capability. Evaluate north-south, east-west, node-local, Kubernetes-control, non-network, controller-mediated, SDK-mediated, storage, and managed-service paths independently.

## Final outputs

Final delivery must contain exactly two human-readable Chinese Markdown reports:

```text
{report_dir}/component-boundary-scan.md
{report_dir}/candidate-vulnerabilities.md
```

Do not emit separate human-readable Stage B/C/D reports such as interface-binding-map, reachability-map, identity-policy-map, runtime-privilege-map, gpu-device-node-boundary-map, parameter-propagation-map, resource-ownership-map, integration-delta, verification-plan, or cve-triage.

The analysis may still use the corresponding concepts and internal structured notes. When machine-readable handoff data is required by an orchestrator, preserve the existing English schema/IDs/enums internally, but do not treat those artifacts as user-facing final reports unless explicitly requested.

### Report 1: component boundary scan

`component-boundary-scan.md` must summarize only the security-relevant boundary information needed to understand the integration:

1. 扫描对象；
2. 组件接口与能力边界；
3. 集成调用链；
4. 身份与权限边界；
5. 参数与资源边界；
6. 边界扫描结论。

Keep this report concise. Do not enumerate ordinary interfaces that have no security relevance.

### Report 2: candidate vulnerabilities

`candidate-vulnerabilities.md` contains only retained vulnerability candidates worth manual reproduction. Every candidate uses a stable heading:

```markdown
### CAND-AIML-001: <中文候选漏洞标题>
```

Keep metadata minimal:

```text
组件
Taxonomy
严重性
置信度
状态
验证优先级
```

Then include exactly these six substantive sections:

```text
候选漏洞描述
攻击者能力
Root Cause
复现环境
复现步骤
可能影响
```

Do not add separate sections for evidence gaps, false-positive conditions, remediation, expected boundary, observed boundary, or prohibited automated actions. Fold only the essential evidence and boundary difference into `候选漏洞描述` and `Root Cause`.

Sort candidates by `P0 -> P1 -> P2 -> P3`, then by severity and confidence. Keep rejected and low-quality research leads out of the final candidate report.

## Candidate gate

Do not retain a candidate merely because an interface, platform operation, GPU asset, shared identity, or sensitive parameter exists. Require an evidence-backed integration delta and answer:

```text
1. 哪个低权限主体可以触发？
2. 经过哪条真实集成链？
3. 哪个安全边界发生了变化或丢失？
4. 最终到达哪个具体 CIFACE-* / GASSET-* / PSOP-* 或资源？
5. 为什么不是组件独立部署时同样存在的问题？
6. 为什么不是用户显式不安全配置导致？
```

For indirect/delegated integrations, resolve topology, bridge, identity, parameter, and ownership chains enough to state a concrete source -> sink boundary and impact. Plausible but unresolved ideas remain internal research leads.

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
- Do not submit workflows, mutate CRDs/resources, create cloud resources, invoke state-changing service operations, read real tenant artifacts, execute payloads, or bypass live authorization automatically.
- Reproduction steps may describe state-changing or cross-tenant checks only as manual actions for an authorized isolated test environment using synthetic resources.
- Every candidate must cite enough source/configuration/contract evidence in `候选漏洞描述` or `Root Cause` to support the integration chain and boundary claim.
- Do not treat shared ServiceAccounts, IAM `PassRole`, privileged workloads, assigned GPU access, or dangerous operations alone as proof of a vulnerability.
- Call outputs candidates until authorized manual verification confirms the claim.
- Distinguish component behavior, adapter/controller behavior, platform/service root cause, deployment/policy misconfiguration, and shared ownership.
