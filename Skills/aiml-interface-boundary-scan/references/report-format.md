# 中文源码扫描报告格式

## Output contract

Write exactly two human-readable reports:

```text
{report_dir}/component-boundary-scan.md
{report_dir}/candidate-vulnerabilities.md
```

Use Chinese prose. Preserve IDs, enums, product names, API and resource names, symbols, paths, versions, ARNs, and URIs in their original form.

## Report 1: component-boundary-scan.md

```markdown
# 组件集成安全边界源码扫描报告

## 1. 扫描对象与版本

- 平台:
- 第三方组件:
- 集成模式:
- 源码与配置 revision:

## 2. 扫描范围与证据覆盖

列出 source role、path class、已评估状态、排除范围和残留 gap。

## 3. 威胁模型

说明租户用户、tenant workload、ServiceAccount、Controller/cloud identity、node-local actor 的起始能力和信任边界。

## 4. 组件安全相关接口与目标

只列安全相关的 CIFACE-*、GASSET-* 和 PSOP-*。

## 5. 集成调用链

概括关键 invocation、parameter、identity、resource ownership 和 runtime privilege 链。

## 6. 身份与权限边界

说明身份保持、丢失、共享、放大、角色委托和授权位置。

## 7. 参数与资源边界

说明安全敏感字段、验证点、授权点、sink 和所有权关系。

## 8. GPU、运行时与节点边界

不适用时给出证据支持的 not_applicable；适用时总结必要边界。

## 9. 扫描缺口

区分整体覆盖缺口和影响具体候选的缺口。

## 10. 候选问题摘要

只索引最终候选 ID、标题、状态和人工验证优先级。
```

## Report 2: candidate-vulnerabilities.md

Include only `source_supported_candidate` and `deployment_dependent_candidate`. Sort by `P0 -> P1 -> P2 -> P3`, preliminary severity, confidence, and stable ID.

Use this template for every candidate:

```markdown
### CAND-AIML-001: <中文候选问题标题>

- 平台:
- 第三方组件:
- 受影响版本或 revision:
- 主要边界类型:
- 次要标签:
- 目标: <CIFACE-* | GASSET-* | PSOP-*>
- 候选状态: <source_supported_candidate | deployment_dependent_candidate>
- 初步严重性: <Critical | High | Medium | Low>
- 源码置信度: <High | Medium>
- 人工验证优先级: <P0 | P1 | P2 | P3>

#### 1. 漏洞信息

说明正常预期边界、源码显示的集成后边界变化、具体问题和集成相关性。始终称为候选，不写“已确认漏洞”。

#### 2. 攻击者能力与前置条件

说明最低权限主体、起点、可控输入、已有凭据，以及不需要具备的高权限。单列尚待确认的部署条件。

#### 3. 源码证据与集成链

给出 source -> bridge/dispatcher -> guard or missing guard -> target 链，引用 revision、文件、symbol/line、配置路径和稳定证据 ID。

#### 4. Root Cause

定位具体代码、策略、默认配置或契约错配，并区分 platform、component、adapter/controller、deployment 或 shared responsibility。

#### 5. 人工验证环境

列出最小隔离环境、版本、部署模式、测试租户、合成数据、RBAC/IAM、网络和 GPU 配置要求。

#### 6. 人工验证步骤

给出编号步骤。先验证配置和可达性，再验证身份/参数传播、授权点和对合成测试资源的结果。不要要求在生产或真实租户资源上执行。

#### 7. 验证判定标准

- 支持候选的正向信号:
- 排除或降级候选的反向信号:
- 需要收集的证据:

#### 8. 可能影响

说明成功后具体的机密性、完整性、可用性、执行、跨租户、GPU、节点或控制面影响；区分默认影响和依赖额外条件的影响。

#### 9. 安全限制

列出禁止自动或在生产环境执行的状态改变、跨租户、驱动/kernel、GPU memory、fabric 或破坏性动作。
```

## Language and claim rules

- Use “候选问题” or “候选漏洞”, never “已确认漏洞”.
- Use “初步严重性”, not a claimed CVSS score.
- Do not label a candidate 0-day, CVE-eligible, exploitable, or disclosure-ready.
- Do not hide evidence gaps or falsification conditions from the manual reviewer.
- Do not place research leads, rejected items, generic hardening advice, or unrelated standalone component defects in the candidate report.
