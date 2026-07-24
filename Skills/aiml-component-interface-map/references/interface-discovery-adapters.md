# Interface Discovery Adapters

Apply every adapter matching the component. These are search seeds, not proof of reachability.
Trace every match to or from a registration root and record additional project-specific patterns.

## Python web and RPC

| Stack | Search seeds |
| --- | --- |
| FastAPI / Starlette | `FastAPI(`, `APIRouter(`, `@app.get`, `@app.post`, `@router.`, `include_router`, `add_api_route`, mounts, lifespan |
| Flask | `Flask(`, `@app.route`, `@blueprint.route`, `add_url_rule`, `register_blueprint` |
| aiohttp | `web.Application`, `RouteTableDef`, `@routes.`, `add_routes`, `router.add_` |
| Django / DRF | `urlpatterns`, `path(`, `re_path(`, `include(`, routers, viewsets, ASGI/WSGI entrypoints |
| gRPC Python | `*_pb2_grpc`, `add_*Servicer_to_server`, `grpc.server`, `grpc.aio.server` |

Also search framework middleware and mount order; authentication on one application/router does not
prove coverage of separately mounted stacks.

## Go web, gRPC, and Kubernetes

Search `net.Listen`, `http.Server`, `ListenAndServe`, `ServeMux`, `Handle`, `HandleFunc`, Gin route
methods/groups, Chi `Route`/`Mount`, Gorilla routers, `grpc.NewServer`, `Register*Server`,
`RegisterService`, reflection, and gateway translation.

For controller-runtime/operator components, search:

```text
SetupWithManager
For / Owns / Watches
Reconcile
NewWebhookManagedBy
WithDefaulter / WithValidator
CustomResourceDefinition
rbac markers
ServiceAccount / Role / ClusterRole
```

Treat CRDs, subresources, admission webhooks, controllers, and service-account-mediated actions as
interfaces even when no ordinary HTTP route exists.

## C++ and TensorFlow Serving

Search `.proto` `service` and `rpc` declarations, generated service bases, `RegisterService`,
`AddListeningPort`, HTTP/REST translation, server constructors, monitoring handlers, CLI flags,
server options, build tags, and configuration files.

For TensorFlow Serving, separately enumerate `PredictionService`, `ModelService`, REST translations,
model status/reload configuration operations, and monitoring/metrics. Trace which options enable
each listener and operation.

## TensorBoard

Search `TBPlugin`, `get_plugin_apps()`, plugin loaders/registries, data providers, WSGI application
construction, path prefix handling, dynamic route dictionaries, static frontend routes, and
frontend-to-backend API calls.

Enumerate each plugin's dynamically registered routes. A scan of ordinary decorators alone is
incomplete when the plugin registry was not expanded.

## Specs and cross-language registration

Always search OpenAPI/Swagger documents, protobufs, GraphQL schemas/resolvers, WebSocket upgrades,
SSE content types, webhook configuration, CLI help/defaults, config schemas, Helm/manifests shipped
by the component, Unix sockets, database migrations/protocol clients, object-store prefixes, and
filesystem watchers.

## Exclusion discipline

Do not silently drop client SDK methods, test servers, examples, generated code, deprecated APIs, or
build-tagged implementations. Classify and count them as excluded or conditional, with evidence.
