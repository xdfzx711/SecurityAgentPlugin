# SecurityAgentPlugin

A collection of skills for evidence-backed security analysis, with a structured AI/ML component integration pipeline.

## Project Structure

```text
SecurityAgentPlugin/
  Skills/
    aiml-component-interface-map/
    aiml-interface-boundary-scan/
    security-scan/
```

## Skills

- **aiml-component-interface-map** - Stage A standalone component discovery. Enumerates network and non-network interfaces, listeners, registration paths, security contracts, planes, dangerous operations, and completeness evidence without analyzing a platform integration.
- **security-scan** - General multi-agent vulnerability scanning with structured discovery, verification, and validation for codebases.
- **aiml-interface-boundary-scan** - Stages B–D platform integration analysis. Consumes a Stage A baseline and resolves direct or indirect integration topology, interface/platform-operation bindings, reachability/invocation, identity/policy/delegation, parameter propagation, ownership, runtime/GPU privilege deltas, candidate vulnerabilities, verification plans, and CVE/disclosure priority.

## AI/ML Integration Security Pipeline

```text
Stage A: Third-party component source
  -> Component Interface Baseline

Stage B: Baseline + integration evidence
  -> Integration Topology
  -> Interface / Platform-Operation Binding
  -> Reachability / Invocation
  -> Identity / Policy / Delegation
  -> Parameter / Resource Ownership Mapping

Stage C: Component contract vs effective integration state
  -> Integration Delta + Candidate Vulnerabilities

Stage D: Authorized manual verification
  -> Verification Result + CVE/Disclosure Triage
```

The central separation is:

```text
Know the Component -> Know the Integration -> Find the Security Delta
```

Version 6 expands Stage B beyond direct source-level bindings. An integration may be resolved through evidence-backed adapters, CRDs, controllers/operators, SDK calls, managed-service APIs, identities, policies, storage handoffs, or generated resources. The declared platform may be a downstream managed execution backend while the declared component acts as the orchestrator.

Default report layout:

```text
reports/
  stage-a-component-baseline/
    component-interface-map.md
    interface-map.yaml
    coverage-report.md
  stage-b-platform-integration/
    interface-binding-map.md
    reachability-map.md
    identity-policy-map.md
    runtime-privilege-map.md
    gpu-device-node-boundary-map.md
    parameter-propagation-map.md
    resource-ownership-map.md
    platform-integration.yaml
  stage-c-security-delta/
    integration-delta.md
    candidate-vulnerabilities.md
    security-delta.yaml
  stage-d-verification/
    verification-plan.md
    cve-triage.md
    verification-triage.yaml
```

`aiml-interface-map` was renamed to `aiml-component-interface-map` in version 2.0. Stage B does not re-enumerate component interfaces; callers pass the Stage A `interface-map.yaml`.

## Status

Under active development.

## License

MIT
