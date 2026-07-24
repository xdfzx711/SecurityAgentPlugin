# Component Interface Workflow

## Purpose

Produce a reusable standalone component baseline that a later platform scan can consume without
rescanning the component. The unit of evidence is the registration path from an externally
consumable root to a concrete operation.

## 1. Freeze the component identity

Record name, semantic version, Git commit, image reference and digest when available. Record the
source roots, build tags, packaging profile, default CLI arguments, and default configuration used
for the scan. Never merge evidence from incompatible versions without labeling it.

## 2. Discover registration roots

Search server entrypoints, constructors, default ports, CLI flags, configuration schemas, manifests,
generated protobuf registration, plugin registries, controllers, and webhooks.

Create a listener record for each root:

```yaml
listener_id: CLISTENER-TFS-001
process: tensorflow_model_server
surface_kind: network
protocol: gRPC
bind_address: "0.0.0.0"
port: 8500
enabled_by_default: true
registration_source:
  file: tensorflow_serving/model_servers/server.cc
  symbol: Server::BuildAndStart
```

For non-network roots, use a meaningful protocol and locator: `Kubernetes`, `filesystem`, `S3`,
`SQL`, or `library`, with port set to `not_applicable`.

## 3. Walk top-down

For every root, trace:

```text
Listener / registration root
  -> router, service, registry, controller, or dispatcher
  -> handler, RPC, reconcile action, or operation
```

Record conditional registration and aliases. Expand generated definitions back to their source
OpenAPI/protobuf/CRD schema. Do not treat frontend pages as proof that their backend operations were
enumerated.

## 4. Search bottom-up

Search the full component source for handler and operation patterns independently of the discovered
roots. Use the relevant framework adapters. Include:

- route decorators and router registration;
- protobuf `service`/`rpc` and `Register*Server`;
- WebSocket/SSE handlers and upgrade paths;
- plugin hooks and dynamic route registries;
- webhooks, CRDs, reconcilers, watches, and service-account-mediated actions;
- filesystem, object-store, database, and library contracts;
- feature flags and alternate server stacks.

Classify each result as reachable from a root, configuration-gated, generated/client-only,
test/example-only, deprecated, or unresolved.

## 5. Reconcile

Cross-check:

- listeners against documented/default ports and startup flags;
- router registrations against concrete handlers;
- protobuf services against server registration;
- frontend calls against backend routes;
- configuration keys against gated interfaces;
- top-down operations against reverse-search results.

Deduplicate aliases without losing protocol variants. REST and gRPC operations with equivalent
semantics remain separate interface records when policy can cover them differently.

## 6. Classify the interface

Use one primary family:

`API`, `Dashboard`, `Runtime`, `Model Serving`, `Artifact`, `Storage`, `Telemetry`, `Streaming`,
`Management`, `Auth/Admin`, `Proxy`, or `Orchestration / Kubernetes Control`.

Use one `surface_kind`:

`network`, `kubernetes_resource`, `filesystem`, `object_store`, `webhook`, `controller`, `database`,
or `library_api`.

Use one `plane`:

- `data`: normal workload/data consumption, such as inference.
- `control`: workload or resource lifecycle control.
- `management`: component administration, configuration, repository lifecycle, or global state.
- `telemetry`: metrics, logs, traces, health, and operational observation.
- `mixed`: inseparable operations from more than one plane; explain why.

Do not use `mixed` merely because classification is uncertain.

## 7. Derive the security contract

Derive only component-native facts:

- intended consumer;
- built-in authentication and authorization;
- tenant awareness;
- expected network or resource scope;
- default protection assumption.

Evidence priority is source/default configuration, normative specification, official documentation,
then inference. For an inference, label `evidence_type: inference` and state the reasoning. Absence
of auth middleware is evidence for `absent` only after all registration stacks were checked.

## 8. Run the completeness gate

Populate the coverage object from the schema. Set:

- `substantially_complete` only when all mandatory checks are true or justified `not_applicable`,
  reconciliation has no unexplained interfaces, and residual gaps do not hide an entire listener,
  router stack, protocol, plugin system, or configuration profile.
- `incomplete` when any mandatory discovery path is unexamined, source/version evidence is missing,
  dynamic registration is unresolved, or top-down and bottom-up results conflict.

The coverage report and YAML `discovery_checks` records must include:

| Check | Result | Evidence | Residual gap |
| --- | --- | --- | --- |
| Listener discovery | pass/fail/n-a | file/symbol/config | exact gap |
| Router/service discovery | pass/fail/n-a | evidence | exact gap |
| Handler/RPC enumeration | pass/fail/n-a | evidence | exact gap |
| Dynamic registration | pass/fail/n-a | evidence | exact gap |
| Proto services | pass/fail/n-a | evidence | exact gap |
| Feature/config flags | pass/fail/n-a | evidence | exact gap |
| Reverse search | pass/fail | patterns and roots | exact gap |
| Cross-check | pass/fail | reconciliation counts | exact gap |

Include counts for discovered listeners, route stacks, interfaces, unmatched top-down results,
unmatched bottom-up results, and exclusions. Give every gap a stable `CGAP-*` ID and affected
listener, interface, protocol, surface, profile, or source-root scope so Stage B can propagate it.

## TensorFlow Serving acceptance profile

For a TensorFlow Serving baseline, explicitly reconcile:

- gRPC listeners and registrations for `PredictionService` and `ModelService`;
- each RPC, including prediction and configuration/model-status operations;
- REST translation routes and their mapping to prediction operations;
- monitoring/metrics configuration and endpoints;
- server options and CLI/configuration conditions that enable or change interfaces.

The result must distinguish inference data-plane operations from model status/reload management or
control operations. Missing one of these groups forces `coverage_status: incomplete`.
