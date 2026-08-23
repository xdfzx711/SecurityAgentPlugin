# 中文安全扫描报告格式

本文件规定 `aiml-interface-boundary-scan` 的人类可读 Markdown 报告格式。除稳定 ID、枚举值、协议名、API/资源名、CWE/CVSS、源码符号和必要的英文产品名外，报告正文默认使用中文。

## 1. 总体要求

Stage A–D 的 Markdown 报告默认使用中文说明。YAML handoff 继续保留既有英文 schema、ID 与 enum，不翻译字段名和枚举值。

Stage C 的 `{report_dir}/stage-c-security-delta/candidate-vulnerabilities.md` 必须使用本文件规定的候选漏洞模板。不得用自由散文替代模板，也不得因为信息缺失而省略字段或章节。

规则：

- 按 `验证优先级` 从 P0、P1、P2、P3 排序；同优先级按风险和置信度排序。
- 标题必须说明“默认/推荐条件 + 暴露或边界问题 + 关键对象”，避免笼统标题如“权限问题”。
- `Taxonomy` 可列多个 A1–A9，但第一个必须是主要分类。
- `漏洞类型` 使用通用安全术语，例如 Missing Authentication、Broken Access Control、Confused Deputy、Improper Authorization、Cross-Tenant Access、Excessive Privilege Delegation。
- `CWE` 只有在语义确实匹配时填写；不确定时写 `待确认`，不得为了完整性强行映射。
- `严重性` 使用 `Critical | High | Medium | Low | Informational`。
- `评分` 使用 0.0–10.0；如果尚不能可靠评分，写 `待验证后评分`。如使用 CVSS，应在正文证据中注明版本和 vector。
- `置信度` 使用 `High | Medium | Low`。
- `状态` 优先使用既有状态，例如 `candidate_requires_manual_validation`、`confirmed_by_non_destructive_probe`、`research_only`、`rejected_contextual`。
- `验证优先级` 使用 `P0 | P1 | P2 | P3`：P0 表示应最先人工验证，P3 表示低优先级研究线索。
- 不得把推测写成已经确认的事实。条件性影响必须明确写“若……则……”。
- 每个关键结论应能回溯到源码、部署配置、官方文档、策略对象或授权的只读观察。
- 章节不得留空。如果当前没有信息，明确写 `暂无已确认内容`、`未发现关键缺口` 或 `待人工验证`。

## 2. 报告开头

`candidate-vulnerabilities.md` 开头使用简短扫描摘要：

```markdown
# AI/ML 平台组件集成安全扫描报告

## 扫描摘要

- 平台: <平台名称>
- 平台版本/部署版本: <版本、commit、chart、unknown>
- 第三方组件: <组件名称>
- 组件版本: <版本、image、digest、commit>
- 集成模式: <integration_modes>
- 扫描范围: <源码、配置、CRD、Controller、SDK、IAM/RBAC、API contract 等>
- Stage A 基线: <baseline id / coverage status>
- 候选漏洞数量: <数量>
- P0/P1/P2/P3: <数量统计>

---
```

摘要只写必要信息，不在这里重复每个候选的详细内容。

## 3. 单个候选漏洞强制模板

每个候选必须严格按以下顺序输出：

```markdown
### CAND-AIML-001: 默认 NodePort 暴露未启用后端认证的 MLflow UI/API

- 组件: MLflow Server
- 组件版本: 2.22.0 image `docker.io/charmedkubeflow/mlflow:2.22.0-5be7a7a`
- Taxonomy: A6 Deployment Default Exposure, A1 Management API Boundary Bypass
- 接口: `NodePort 31380 -> mlflow_port 5000`, `/`, `/api/2.0/mlflow/*`
- 协议/方法: HTTP GET/POST 等 MLflow REST/UI
- 漏洞类型: Missing Authentication / Exposed Management API / Broken Access Control
- CWE: CWE-306, CWE-862
- 影响边界: 外部或节点网络访问边界、MLflow tracking/model registry 管理边界
- 严重性: High
- 评分: 8.2
- 置信度: High
- 状态: candidate_requires_manual_validation
- 验证优先级: P0

#### 预期边界

说明组件自身安全契约、平台租户模型或官方部署模型原本应维持的安全边界。必须具体到主体、对象和权限范围，例如“仅所属 namespace 的 Pipeline ServiceAccount 可创建本租户对应的 SageMaker CR”。

#### 观察边界

说明实际集成后观察到的有效边界，以及它与预期边界的差异。优先采用 source -> bridge -> identity/policy -> sink 的形式描述，不要只写“可能越权”。

#### 当前证据

逐条列出已经取得的证据。至少包含定位信息和它证明的事实，例如：

- `path/file.yaml:42-58`：创建 `NodePort` 并暴露端口 31380。
- `server/auth.py:<symbol>`：默认路径未启用后端认证中间件。
- 官方部署文档 `<section>`：该 Service/RoleBinding 属于默认或推荐部署路径。

只写当前实际存在的证据，不要把计划验证的内容写进这里。

#### 证据缺口

明确列出仍阻止最终确认、评分或归责的关键事实，例如：

- 尚未确认默认 NetworkPolicy 是否阻止普通租户 Pod 到该 Service 的访问。
- 尚未确认目标版本是否默认授予 `iam:PassRole` 到用户可选 roleArn。

如果不存在关键缺口，写：`未发现影响当前结论的关键证据缺口。`

#### 可能影响

说明成功跨越边界后能够产生的具体安全影响。区分已由证据支持的默认影响与需要额外条件的条件性影响。

禁止把“存在危险 API”“存在共享 ServiceAccount”“存在 iam:PassRole”本身写成最终影响。

#### 误报条件

列出会推翻、降级或重新归类该候选的条件，例如后端存在未发现的 object-level authorization、默认 NetworkPolicy 完整阻断路径、所需 IAM 权限只存在于用户显式不安全配置等。

#### 安全验证建议

给出最小、可重复、非破坏性的人工验证步骤。优先验证：

1. 路径是否真实可达；
2. 实际使用的身份；
3. 授权点是否检查 tenant/object/resource scope；
4. 是否在官方默认/推荐部署下成立；
5. 使用合成测试资源验证跨边界行为。

验证建议不得要求读取真实租户数据或直接破坏生产资源。

#### 禁止自动执行的危险步骤

明确列出扫描器不得自动执行的状态改变或高风险动作，例如：

- 不自动创建、删除、停止或更新真实训练任务/模型/Endpoint；
- 不自动调用 model load/unload、job cancel/delete 等管理操作；
- 不自动尝试跨租户读取真实 artifact、secret 或日志；
- 不自动修改 RBAC/IAM/CRD/NetworkPolicy；
- 不自动利用节点、GPU、driver、kernel 或云身份权限进行提权。

#### 修复建议

给出与根因对应的修复，而不是泛化建议。优先说明应该在哪个边界实施：

- 缩小 Service/Ingress/NetworkPolicy 暴露；
- 在后端增加 authentication / object-level authorization；
- 绑定 tenant/namespace/object owner；
- 使用 per-tenant ServiceAccount / workload identity；
- 限制 `iam:PassRole`、AWS resource ARN、S3 prefix、KMS key 等可选范围；
- 在 adapter/controller admission/reconcile 层验证安全敏感字段；
- 为管理接口和普通数据面建立独立策略。
```

字段内容应根据候选实际情况替换，不要机械保留示例中的 MLflow 名称或数值。

## 4. Evidence ID 与正文

如果 Stage B/C YAML 已生成 `EVID-*`、`BIND-*`、`IBRIDGE-*`、`PFLOW-*`、`ICHAIN-*`、`RBIND-*`、`DELTA-*` 等 ID，可在“当前证据”和“观察边界”中括号引用，例如：

```text
KFP 参数 `roleArn` 经 `IBRIDGE-SM-KFP-001` 到达 `PSOP-SAGEMAKER-001`，对应 `PFLOW-SM-KFP-003`。
```

人类可读报告应优先解释事实，ID 用于回溯，不能只堆 ID 而不给中文说明。

## 5. research_only 和 rejected 的格式

`research_only` 仍使用同一模板，但必须在“证据缺口”中说明为什么不能提升为候选；`严重性` 和 `评分` 可以写 `待验证`。

已拒绝的条目默认不混入主要候选漏洞列表。可以在报告末尾增加：

```markdown
## 已降级或排除的问题

- `CAND-AIML-00X`：<简要标题> — <rejected_contextual / research_only>，原因：<一句话>。
```

不要让大量低质量 research leads 淹没 P0/P1 候选。

## 6. 报告语言与术语

中文是默认输出语言，但以下内容保持原始形式：

- `CAND-*`、`CIFACE-*`、`GASSET-*`、`PSOP-*` 等稳定 ID；
- A1–A9 taxonomy 英文名称；
- API、HTTP method、CRD kind、IAM action、Kubernetes resource、源码 symbol；
- CWE/CVSS；
- 产品、镜像、版本、路径、ARN、URI。

推荐写法：

```text
- Taxonomy: A7 Identity Propagation Mismatch
- 漏洞类型: Confused Deputy / Improper Authorization
- 影响边界: Kubeflow namespace 租户边界 -> ACK controller 共享 AWS IAM 权限边界
```

避免把所有专业术语强行翻译后导致与源码和官方文档无法对应。
