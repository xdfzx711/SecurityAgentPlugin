# 中文安全扫描报告格式

本文件规定 `aiml-interface-boundary-scan` 的最终报告格式。

## 1. 输出原则

最终交付物严格只输出两个中文 Markdown 报告：

```text
{report_dir}/component-boundary-scan.md
{report_dir}/candidate-vulnerabilities.md
```

不要再单独输出 interface binding、reachability、identity policy、runtime privilege、GPU boundary、parameter flow、resource ownership、integration delta、verification plan、CVE triage 等人类可读报告。分析过程中仍应完成这些检查，但把必要结论压缩到上述两个文件中。

除稳定 ID、enum、API/资源名、CWE/CVSS、源码符号、产品名、路径、ARN、URI 等需要保持原文的内容外，正文使用中文。

不要为了“完整”重复同一事实。一个证据只在最能说明问题的位置出现一次。

---

## 2. 报告一：组件边界扫描

文件：

```text
{report_dir}/component-boundary-scan.md
```

目标：用一个报告说明组件自身安全边界，以及组件接入平台后的实际安全边界。

建议固定为以下结构：

```markdown
# 组件边界扫描报告

## 1. 扫描对象

- 平台: <名称/版本>
- 第三方组件: <名称/版本>
- 集成模式: <direct / workflow_adapter / crd_controller_delegate / sdk / managed service 等>
- 扫描范围: <主要源码、部署配置、Controller、CRD、IAM/RBAC、API contract>

## 2. 组件接口与能力边界

用表格或精简条目列出真正与安全相关的接口/能力：

| 接口/对象 | 类型 | 调用方 | 认证/授权 | 危险能力 | 默认暴露范围 |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

只列安全相关接口，不要把所有普通接口机械展开。

## 3. 集成调用链

给出实际 integration chain，例如：

`KFP User -> Pipeline Component -> SageMaker CR -> ACK Controller -> AWS IAM -> SageMaker API`

对于每条关键链，说明：

- source：谁能够触发；
- bridge：经过什么 Adapter / CRD / Controller / SDK；
- identity：最终使用什么身份；
- sink：最终能够操作什么组件或平台资源。

## 4. 身份与权限边界

只总结关键身份转换和授权点，例如：

- 用户身份是否折叠为共享 ServiceAccount；
- namespace/tenant context 是否继续保留；
- Controller 是否使用共享云身份；
- 是否存在 `iam:PassRole`、ClusterRole、跨 namespace 或跨资源权限；
- object owner / tenant 是否在最终授权点被检查。

## 5. 参数与资源边界

只列可能改变安全边界的字段与资源，例如：

- roleArn / execution role；
- S3 bucket/prefix；
- ECR image；
- KMS key；
- VPC/subnet/security group；
- Job/Model/Endpoint/resource ARN；
- 管理接口、artifact、GPU/node 资源。

说明这些值从哪里进入、最终到哪里、在哪个位置验证或授权。

## 6. 边界扫描结论

用简短列表总结：

- 已确认保持的安全边界；
- 发生身份、权限、暴露面或资源所有权变化的边界；
- 已进入候选漏洞报告的高风险问题编号。
```

该报告的目标是“看懂系统边界”，不是复述整个扫描过程。

---

## 3. 报告二：候选漏洞详细信息

文件：

```text
{report_dir}/candidate-vulnerabilities.md
```

只输出达到候选门槛、值得人工复现的问题。低质量 research lead、已排除问题和普通加固建议不要进入主报告。

候选按 `P0 -> P1 -> P2 -> P3` 排序，同级优先风险更高、证据更充分的问题。

每个候选使用以下精简模板：

```markdown
### CAND-AIML-001: <中文候选漏洞标题>

- 组件: <组件名称和版本>
- Taxonomy: <A1-A9，可多个，主要分类放第一位>
- 严重性: <Critical | High | Medium | Low>
- 置信度: <High | Medium | Low>
- 状态: <candidate_requires_manual_validation | confirmed_by_non_destructive_probe | research_only>
- 验证优先级: <P0 | P1 | P2 | P3>

#### 候选漏洞描述

用 1-3 段说明：正常预期边界是什么、实际集成后发生了什么变化、攻击者可能因此获得什么原本不应有的能力。

必须给出关键 source -> bridge -> authorization -> sink 链路，并引用最重要的源码/配置/官方契约定位。不要单独再创建“当前证据”“观察边界”等章节。

#### 攻击者能力

明确最低攻击者前置能力，例如：

- 普通 Kubeflow tenant/user；
- 可提交 PipelineRun 的 namespace 用户；
- 已获得合法 GPU workload 代码执行权限的租户；
- 可控制某个组件输入参数，但没有平台管理员权限。

同时说明攻击者不需要具备的高权限，避免把管理员能力误写成漏洞。

#### Root Cause

说明根因发生在哪一层以及为什么产生安全边界漂移，例如：

- Adapter 未绑定 tenant/object owner；
- CRD 字段直接传播到云 API；
- Controller 使用共享高权限 IAM role；
- 后端管理接口缺少认证或 object-level authorization；
- RBAC / IAM / NetworkPolicy 只覆盖部分路径；
- 平台把多个用户身份折叠为同一执行身份。

必须尽量定位到具体源码函数、配置项、manifest、policy 或 API contract。

#### 复现环境

写清最小可复现环境：

- 平台及版本；
- 组件及版本/image/commit；
- 相关部署方式；
- 必要的 ServiceAccount、RBAC/IAM、CRD、NetworkPolicy 或云资源条件；
- 使用测试租户/测试资源，不使用真实生产租户数据。

#### 复现步骤

给出最小、可重复的人工验证步骤，按编号列出。

步骤应优先验证：

1. 攻击者是否能够到达入口；
2. 输入/身份如何沿集成链传播；
3. 最终授权点是否缺少预期的 tenant/object/resource scope 检查；
4. 是否能够对合成测试资源产生预期的越界结果。

Skill 本身不得自动执行破坏性或跨租户利用行为。状态改变、云资源创建/删除、跨租户访问等步骤只作为授权测试环境中的人工复现建议。

#### 可能影响

说明成功利用后能够造成的具体结果，例如：

- 跨租户读取、修改、删除或引用资源；
- 选择超出当前租户权限范围的执行角色；
- 操作训练任务、模型、Endpoint 或管理 API；
- 访问或覆盖其他租户 artifact；
- 获得节点/GPU/云资源级额外能力；
- 泄露敏感配置、日志或元数据。

区分默认即可达到的影响与依赖额外条件的影响，不要夸大。
```

---

## 4. 候选门槛

不要因为存在危险 API、共享 ServiceAccount、`iam:PassRole`、NodePort、ClusterRole、GPU device 或 Controller 权限就直接生成候选。

候选至少需要回答：

```text
1. 哪个低权限主体可以触发？
2. 经过哪条真实集成链？
3. 哪个安全边界发生了变化或丢失？
4. 最终到达哪个具体接口/平台操作/资源？
5. 为什么不是组件独立部署时同样存在的问题？
6. 为什么不是用户显式不安全配置导致？
```

无法回答这些问题的内容保留为内部研究线索，不进入最终候选漏洞报告。

## 5. 语言与引用

中文是默认输出语言，但以下内容保持原始形式：

- `CAND-*`、`CIFACE-*`、`GASSET-*`、`PSOP-*`、`IBRIDGE-*` 等稳定 ID；
- A1-A9 taxonomy 英文名称；
- HTTP method、API、CRD kind、IAM action、Kubernetes resource、源码 symbol；
- CWE/CVSS；
- image、version、path、ARN、URI。

优先用具体代码/配置定位支撑 Root Cause 和复现链路，避免大段泛化描述。