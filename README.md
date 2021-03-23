# Magenta Voice Skill SDK

Magenta Voice Skill SDK for Python is a package that assists in creating Voice Applications for Magenta Voice Platform.

## About

This is a reworked stack supporting explicit `async/await` concurrency
and based on [**FastAPI**](https://fastapi.tiangolo.com/) ASGI framework.

Old stable (Bottle/Gevent) 0.xx [branch](https://github.com/telekom/voice-skill-sdk/tree/stable)

## Installation

### Runtime
Runtime installation: `python -m pip install skill-sdk`.

### Runtime (full)
Runtime installation with Prometheus metrics exporter and distributed tracing adapter: `python -m pip install skill-sdk[all]`.

### Development
Development installation: `python -m pip install skill-sdk[dev]`.

## CLI: **vs**

- `vs init`: initialize an empty skill

- `vs run`: deploy the skill in production mode

- `vs develop`: deploy the skill in development mode (with skill Designer UI)

- `vs translate`: extract translatable strings from Python modules. Optionally, download full catalog from text service

- `vs version`: display skill version

## Hello World

```python
from skill_sdk import skill, Response


@skill.intent_handler("HELLO_WORLD__INTENT")
async def handler() -> Response:
    return "Hello World!"

app = skill.init_app()

app.include(handler=handler)
```
