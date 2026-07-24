# SecurityAgentPlugin

A collection of skills for evidence-backed security analysis, with a structured AI/ML component
integration pipeline.

## Project Structure

```text
SecurityAgentPlugin/
  Skills/
    aiml-component-interface-map/
    aiml-interface-boundary-scan/
    security-scan/
```

## Skills

- **aiml-component-interface-map** - Stage A standalone component discovery. Enumerates network and
  non-network interfaces, listeners, registration paths, security contracts, planes, dangerous
  operations, and completeness evidence without analyzing a platform integration.
- **security-scan** - General multi-agent vulnerability scanning with structured discovery,
  verification, and validation for codebases.
- **aiml-interface-boundary-scan** - Stages B–D platform integration analysis. Consumes a Stage A
  baseline to resolve interface bindings, reachability, identity/policy propagation, integration
  deltas, candidate vulnerabilities, verification plans, and CVE/disclosure priority.

## AI/ML Integration Security Pipeline

```text
Stage A: Third-party component source
  -> Component Interface Baseline

Stage B: Baseline + platform source/deployment
  -> Interface Binding + Reachability + Identity/Policy Maps

Stage C: Component contract vs platform state
  -> Integration Delta + Candidate Vulnerabilities

Stage D: Authorized manual verification
  -> Verification Result + CVE/Disclosure Triage
```

The central separation is:

```text
Know the Component -> Know the Integration -> Find the Security Delta
```

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

`aiml-interface-map` was renamed to `aiml-component-interface-map` in version 2.0. Stage B no longer
re-enumerates component interfaces; update callers to pass the Stage A `interface-map.yaml`.

## Status

Under active development.

## License

MIT
