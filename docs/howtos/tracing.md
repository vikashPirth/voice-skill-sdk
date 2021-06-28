# Distributed Tracing 

Skill SDK for Python equipped with [opentracing](https://opentracing.io/docs/overview/what-is-tracing/) 
adapter to support distributed tracing and logging.

# External Tracer

To plug-in an external opentracing-compatible tracer into the adapter, 
create your tracer instance and call `skill_sdk.middleware.tracing.setup` 
to attach the instance to your skill application.

Here is a sample code for [Jaeger client for Python](https://github.com/jaegertracing/jaeger-client-python):

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
    # Important to explicitly create a ContextVarsScopeManager scope manager: 
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
