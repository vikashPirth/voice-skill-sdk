# Distributed Tracing 

Skill SDK for Python equipped with [opentracing](https://opentracing.io/docs/overview/what-is-tracing/) 
adapter to support distributed tracing and logging.

# `start_span`

`skill_sdk.middleware.tracing.start_span` is a context manager and decorator to create tracing spans (units of work). 

To start a new span with function call, decorate the function with @start_span decorator:


```python
from skill_sdk.middleware.tracing import start_span

@start_span(operation_name='my-operation')
def your_function():
    pass
```

New tracing span with operation name _my-operation_ will be created when you call `your_function` and ended when function returns.

Here is a sample code demonstrating `start_span` as context manager:

```python
from skill_sdk.middleware.tracing import start_span

def your_function():
    
    with start_span(operation_name='my-operation'):
        ...
```


## External Tracer

To plug-in an external opentracing-compatible tracer into the adapter, 
create your tracer instance and call `skill_sdk.middleware.tracing.setup` 
to attach the instance to your skill application.

Here is a sample code for [Jaeger client for Python](https://github.com/jaegertracing/jaeger-client-python):

> Please note to use **ContextVarsScopeManager** or any coroutines-compatible manager to manage tracing storage.   

```python
from skill_sdk import init_app
from skill_sdk.middleware import tracing
from jaeger_client import Config
from opentracing.scope_managers.contextvars import ContextVarsScopeManager

# Jaeger tracer configuration
config = Config(
    config={
        "sampler": {"type": "const", "param": 1},
        "propagation": "b3",
        "logging": False,
    },
    # IMPORTANT: using ContextVarsScopeManager 
    scope_manager=ContextVarsScopeManager(),
    service_name='your-app-name',
)

# this call sets opentracing.tracer
tracer = config.initialize_tracer()

# You skill application instance
app = init_app()

# Plugin the tracer into the app
tracing.setup(app, tracer)
```

## Logging Headers


Skill logging middleware also extracts the following headers, that are used for logging and debugging purposes: 

- `X-B3-TraceId` - distributed trace ID
- `X-B3-SpanId` - distributed span ID
- `X-TenantId` - tenant originating the request
- `X-Testing` - used to separate the real and testing traffic
- `X-User-Debug-Log` - used to temporarily set the logging to DEBUG level  

The headers extracted from skill invoke request, even with no external tracer activated, 
and are propagated to all outgoing skill requests, when using `skill_sdk.requests.Client/AsyncClient` 
with `internal` flag set to `True`:

```python
from skill_sdk.requests import Client

response = Client(internal=True).get("internal-service-url").json()
```
