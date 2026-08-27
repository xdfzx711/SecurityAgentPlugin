# SecurityAgentPlugin

面向 GPU 平台第三方 AI/ML 组件集成的源码安全边界扫描 Skill 集合。

## Project Structure

```text
SecurityAgentPlugin/
  Skills/
    aiml-component-interface-map/
    aiml-interface-boundary-scan/
```

## Skills

- **aiml-component-interface-map**：扫描第三方组件源码和默认配置，建立接口、危险能力、运行时权限和安全假设基线。
- **aiml-interface-boundary-scan**：扫描平台、组件、Adapter、Controller、Operator、SDK、CRD、部署配置和服务契约，发现集成后可能产生的身份、权限、参数、资源、GPU、运行时和节点安全边界变化。

本仓库不提供通用漏洞扫描、自动 PoC、在线攻击验证、CVE 判断或漏洞披露流程。普通代码缺陷只有在真实集成链上造成安全边界变化时，才属于本仓库的扫描范围。

## Source-Scan Pipeline

```text
Stage A: Third-party component source and defaults
  -> Component Interface and Privilege Baseline

Stage B: Platform and integration source/configuration/contracts
  -> Integration Topology
  -> Source / Identity / Parameter / Resource / Privilege Chains

Stage C: Component contract vs statically derived integration state
  -> Source-supported or Deployment-dependent Candidates
  -> Manual Verification Handoff

Out of scope: executing verification or confirming vulnerabilities
```

核心原则：

```text
Know the Component -> Trace the Integration -> Find the Boundary Delta -> Hand Off for Manual Verification
```

## Outputs

默认交付两份中文 Markdown 报告：

```text
reports/
  component-boundary-scan.md
  candidate-vulnerabilities.md
```

扫描过程同时生成可校验的内部状态：

```text
reports/.scan-state/source-scan.json
```

内部状态用于稳定 ID、证据链、覆盖率和人工验证交接，不代替人类可读报告。

## Candidate Meaning

报告中的问题均为源码阶段候选：

- `source_supported_candidate`：源码和默认/推荐配置已经支持完整问题链，仍需人工确认运行时行为与影响。
- `deployment_dependent_candidate`：源码支持问题链，但可利用性依赖实际 RBAC、IAM、网络、运行时或 GPU 部署状态。

候选不得在人工验证前标记为已确认漏洞、0-day 或 CVE。

## Status

Under active development.

## License

MIT
