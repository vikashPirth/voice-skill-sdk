# Magenta Voice Skill SDK

Magenta Voice Skill SDK for Python is a package that assists in creating Voice Applications for Magenta Voice Platform.

## Installation

### Runtime
Runtime install: `python -m pip install skill-sdk`.

### Runtime (with Prometheus metrics exporter and distributed tracing adapter)
Runtime install: `python -m pip install skill-sdk[all]`.

### Development
Development install: `python -m pip install skill-sdk[dev]`.

### Extras requirements

- [all]:
  - `starlette-opentracing` opentracing adapter
  - `starlette-exporter` Prometheus exporter

- [dev]:
  - `starlette-opentracing` opentracing adapter
  - `starlette-exporter` Prometheus exporter

### CLI: **vs**

- `vs init`: initializes an empty skill

- `vs run`: deploys the skill in production mode

- `vs run`: deploys the skill in development mode (with skill Designer UI)

- `vs translate`: extracts translatable strings from Python modules. Optionally, downloads full catalog from text service

- `vs version`: displays skill version
