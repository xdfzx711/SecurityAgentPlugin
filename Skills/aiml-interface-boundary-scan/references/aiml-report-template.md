# AI/ML Interface Boundary Report Template

Use this template for the primary Phase 1 report:

```text
phase1-discovery/ai-ml-candidate-vulnerability-report.md
```

Do not use traditional vulnerability-audit summary metrics such as PoC count, confirmed exploit
count, or 0-day count as the primary report frame. Use interface inventory, deployment context,
boundary mismatches, candidate vulnerabilities, verification plans, and research patterns as the
primary frame.

Write the primary report in Chinese by default unless the user requests another language.

## Phase 1 Report Structure

````markdown
# AI/ML 第三方组件接口边界安全审计报告

## 1. 执行摘要

- 扫描范围: {scope}
- 扫描组件: {component_summary}
- 部署上下文: {deployment_context_summary}
- 暴露接口数量: {interface_count}
- 候选漏洞数量: {candidate_count}
- 高风险边界错位: {highest_risk_boundary_mismatches}
- 当前证据限制: {evidence_limitations}

## 2. 组件与部署上下文

| Component | Version | Role | Deployment | Exposure | Auth Mode | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| {component} | {version} | {role} | {deployment} | {exposure} | {auth_mode} | {evidence} |

## 3. 接口枚举表

| Interface | Component | Route/API | Protocol | Operation | State-changing | Sensitive Output | Expected Boundary | Observed Exposure |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {interface_type} | {component} | `{route_or_api}` | {protocol} | {operation} | {yes_no} | {sensitive_output} | {expected_boundary} | {observed_exposure} |

## 4. 边界模型

| Boundary | Platform Assumption | Component Assumption | Observed Behavior | Mismatch | Evidence |
| --- | --- | --- | --- | --- | --- |
| {boundary_name} | {platform_assumption} | {component_assumption} | {observed_behavior} | {mismatch} | {evidence} |

## 5. 候选漏洞总览

| ID | Title | Taxonomy | Component | Interface | Boundary Violated | Severity | Score | Confidence | Status | Verification Priority |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| CAND-AIML-001 | {title} | A1 | {component} | `{interface}` | {boundary_violated} | High | 8.1 | Medium | candidate_requires_manual_validation | P0 |

## 6. 候选漏洞详情

### CAND-AIML-001: {title}

- 组件: {component}
- 组件版本: {component_version}
- Taxonomy: {A1-A8 or proposed category}
- 接口: `{interface}`
- 协议/方法: {protocol_or_method}
- 漏洞类型: {vulnerability_class}
- CWE: {cwe_when_applicable}
- 影响边界: {boundary_violated}
- 严重性: {severity}
- 评分: {score}
- 置信度: {confidence}
- 状态: {status}
- 验证优先级: {priority}

#### 预期边界

{expected_boundary}

#### 观察边界

{observed_boundary}

#### 当前证据

- {evidence_item_1}
- {evidence_item_2}

#### 证据缺口

- {evidence_gap_1}
- {evidence_gap_2}

#### 可能影响

- {impact_1}
- {impact_2}

#### 误报条件

- {false_positive_condition_1}
- {false_positive_condition_2}

#### 安全验证建议

- {safe_validation_step_1}
- {safe_validation_step_2}

#### 禁止自动执行的危险步骤

- {unsafe_step_1}
- {unsafe_step_2}

#### 修复建议

- {remediation_1}
- {remediation_2}

## 7. Phase 2 验证计划

| Priority | Candidate | Evidence Gap | Safe Verification Method | Required Evidence | Current Status |
| --- | --- | --- | --- | --- | --- |
| P0 | CAND-AIML-001 | {evidence_gap} | {safe_method} | {required_evidence} | not_tested |

## 8. 研究模式总结

### Pattern 1: {pattern_name}

- Observed across: {components_or_candidates}
- Boundary mismatch: {specific_boundary_mismatch}
- Generalized rule: {generalized_rule}
- Example candidates: {candidate_ids}
- Potential taxonomy impact: {taxonomy_impact}
- Evidence strength: {high | medium | low}

## 9. 附录：结构化 YAML

```yaml
components:
  - component: <name>
    version: <version | unknown>
    role: <platform role>
    deployment: <helm | k8s | docker | source | unknown>
    exposure: <public | tenant-facing | internal-only | admin-only | unknown>
    auth_mode: <gateway | oidc | token | basic-auth | none | unknown>
    evidence:
      - <file, route, config, response, package, image>

interfaces:
  - interface_id: IFACE-AIML-001
    component: <component>
    interface_type: <API | Dashboard | Runtime Proxy | Artifact | Telemetry | Management | Model Serving | Storage | Streaming | Auth/Admin>
    route_or_api: <route>
    protocol: <REST | gRPC | WebSocket | SSE | HTTP | S3 | unknown>
    operation: <read | search | submit | cancel | delete | load | unload | logs | metrics | proxy | unknown>
    state_changing: <true | false | unknown>
    sensitive_output:
      - <data type>
    expected_boundary: <expected auth/authz/exposure/trust boundary>
    observed_exposure: <observed behavior>
    evidence:
      - <evidence>

boundary_models:
  - boundary_id: BOUND-AIML-001
    interface_id: IFACE-AIML-001
    platform_assumption: <assumption>
    component_assumption: <assumption>
    observed_behavior: <behavior>
    mismatch: <mismatch>
    evidence:
      - <evidence>

candidate_vulnerabilities:
  - vulnerability_id: CAND-AIML-001
    title: <title>
    taxonomy: <A1-A8 | proposed category>
    component: <component>
    interface_id: IFACE-AIML-001
    boundary_violated: <boundary>
    vulnerability_class: <class>
    cwe:
      - <CWE-ID>
    severity: <critical | high | medium | low | informational>
    score: <0.0-10.0>
    confidence: <high | medium | low>
    status: <candidate_requires_manual_validation | confirmed_by_non_destructive_probe | needs_more_evidence | not_a_vulnerability_contextual>
    evidence:
      - <evidence>
    evidence_gaps:
      - <gap>
    safe_validation:
      - <step>
    false_positive_conditions:
      - <condition>

research_patterns:
  - pattern_id: PATTERN-AIML-001
    name: <pattern name>
    observed_across:
      - <component or candidate>
    boundary_mismatch: <mismatch>
    generalized_rule: <rule>
    example_candidates:
      - CAND-AIML-001
    potential_taxonomy_impact: <impact>
    evidence_strength: <high | medium | low>

proposed_taxonomy_extensions:
  - risk_id: AX
    name: <short name>
    definition: <boundary mismatch definition>
    affected_interfaces:
      - <interface type>
    common_signals:
      - <observable evidence>
    candidate_vulnerability_patterns:
      - Potential <specific issue> in <component/interface>
    validation_focus:
      - <safe validation step>
    false_positive_conditions:
      - <condition>
```
````

## Research Pattern Guidance

The research pattern section is not a restatement of individual findings. It should summarize
reusable boundary-mismatch patterns that can inform future taxonomy or paper writing.

Good pattern examples:

- UI checks object permission, but native API accepts known object IDs directly.
- Platform gateway protects REST routes, but gRPC/WebSocket/SSE route remains uncovered.
- Model deployment permission indirectly grants backend/plugin code execution capability.
- Metrics/logging endpoint leaks cross-tenant GPU/job/runtime metadata.
- Platform authenticates users at the gateway, but backend component receives only service identity.
- Component assumes trusted internal network, but platform exposes it through tenant-facing ingress.

Each pattern should include:

- Pattern ID.
- Pattern name.
- Observed components or candidate IDs.
- Boundary mismatch.
- Generalized rule.
- Evidence strength.
- Potential taxonomy impact.

## Phase 2 Verification Plan Template

When Phase 2 is requested, produce:

```text
phase2-verification/ai-ml-manual-verification-plan.md
```

Use this structure:

```markdown
# AI/ML 第三方组件候选漏洞人工验证计划

## 1. 验证总览

- 候选漏洞数量: {candidate_count}
- P0/P1/P2/P3 分布: {priority_distribution}
- 所需环境: {required_environment}
- 全局安全规则: {global_safety_rules}

## 2. 验证矩阵

| ID | Candidate | Taxonomy | Priority | Environment Needed | Safe Test Available | Destructive Test Needed | Current Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| CAND-AIML-001 | {title} | A1 | P0 | {environment} | Yes | No | not_tested |

## 3. 候选漏洞验证计划

### CAND-AIML-001: {title}

- Taxonomy: {A1-A8 or proposed category}
- 验证优先级: {P0/P1/P2/P3}
- 当前证据: {current_evidence}
- 证据缺口: {evidence_gaps}
- 前置条件: {preconditions}
- 安全验证步骤: {safe_steps}
- 禁止自动执行的危险步骤: {forbidden_steps}
- 预期验证信号: {expected_signals}
- 误报排除条件: {false_positive_conditions}
- 需要收集的证据: {logs_responses_configs_code_paths}
- 验证结论占位: confirmed / false_positive / needs_more_evidence / not_tested
```
