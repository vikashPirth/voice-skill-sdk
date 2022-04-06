
# Changelog
All notable changes to this project will be documented in this file.

## Unreleased

### Bugfixes

- Returning text from nl_build with fullstop in the end.

### Features

- Add data values in the response of version 0

## 1.2.0 - 2022-04-05

### Features

- Enhance User-Agent header to include kubernetes POD name when it comes to SVH cluster requests
- Adding new`ReferenceType` called `MEDIA_CONTENT_END` 

## 1.1.9 - 2022-03-31

### Bugfixes

- Making variable postal_code Optional of class AddressComponents due to some cities from location service has no postal code

## 1.1.8 - 2022-03-17

### Bugfixes

-  FIX Rename Locations timezone to time_zone 

## 1.1.7 - 2022-03-15

### Bugfixes

-  Fix error when returning an instance of Reprompt from an intent handler. 


## 1.1.6 - 2022-02-09

### Features

-   Introduce cvi service-token decryption utility

-   Refactor unit tests from unittest to pytest module. 

### Bugfixes

-   Fixed uvicorn logging when `--log-level` set to `trace`. 

-   Bump FastAPI from 0.68.0 to 0.70.0.

-   Fix mypy error


## 1.1.4 - 2021-08-18

### Features

-   Logging configuration section added to [Deployment guide](docs/deploy.md#deploying-with-gunicorn).    

### Bugfixes

-   Corrected "X-Tenant-Id" tracing header propagation and logging. 

-   Fixed "typing.List" annotation handling in UI.

-   Fixed cutting `DelayedClientTask` from skill response. 
    Added type annotation to `DelayedClientTask.invoke` keyword arguments.

-   Fixed `EntityValueException` if an intent handler parameter annotated as `skill_sdk.intents.Request`.

-   Fixed `ValidationError` when loading skill settings caused by not set API_KEY environment variable.
    
-   Fixed `asyncio - Task exception was never retrieved` error message in debug log UI display.

-   Bump FastAPI from 0.67.0 to 0.68.0.

## 1.1.3 - 2021-07-26

### Bugfixes

-   Fixed persistent service URL in [howto](docs/howtos/persistence_service.md). 

-   Added "skill_id"/"client_type_name"/"user_profile_config" arguments to `create_context` helper. 

-   "Magenta transaction ID" value added to logging record.

-   Bump FastAPI from 0.66.0 to 0.67.0.


## 1.1.2 - 2021-07-12

### Features

-   Added "Baggage-X-Magenta-Transaction-Id" header propagation. The header is also available for logging as:

```python
from skill_sdk.log import tracing_headers

>>> tracing_headers()
{<HeaderKeys.trace_id: 'X-B3-TraceId'>: 'trace-id', <HeaderKeys.span_id: 'X-B3-SpanId'>: 'span-id', <HeaderKeys.tenant_id: 'X-Tenant-Id'>: 'tenant-id', <HeaderKeys.testing_flag: 'X-Testing'>: '1', <HeaderKeys.magenta_transaction_id: 'Baggage-X-Magenta-Transaction-Id'>: 'my-id'}
``` 

### Bugfixes

-   Bump FastAPI from 0.65.2 to 0.66.0. [Release notes](https://github.com/tiangolo/fastapi/releases/tag/0.66.0).

-   Fixed `vs run [module]` command that ignored the _module_ parameter.
    

## 1.1.1 - 2021-06-30

### Features

-   Added [HOWTO](docs/howtos/tracing.md): using opentracing adapter in SDK.


### Bugfixes

-   Fixed `ValidationError` when response contains a client kit command.
    

## 1.1.0 - 2021-06-22

### Features

-   Add support for the new companion app cards format: Action Cards v3.0.


-   When joining internationalization message strings (`i18n.Message`), 
    translation keys are joined along with their values for better readability.


## 1.0.6 - 2021-06-14

### Bugfixes

-   Bump FastAPI from 0.65.1 to 0.65.2. Fixes CSRF vulnerability: [CVE-2021-32677](https://github.com/advisories/GHSA-8h2j-cgx8-6xv7).
    

-   Fix `skill.test_intent` helper FALLBACK_INTENT handling. 


-   Remove `skill.init_app` initialization when running `vs version` command.


## 1.0.5 - 2021-06-07


### Features


- Skill configuration is compatible with [dotenv](https://github.com/theskumar/python-dotenv).
    Skill setting values can be overwritten with environment variables. 
  
    File with environment settings can be specified when running a skill with `--env-file` argument to `vs` CLI tool.
    To start skill in _development_ mode with environment settings loaded from `.env.dev` file:
  
    `vs develop --env-file .env.dev`
    


### Bugfixes

- Various UI [fixes](https://github.com/telekom/voice-skill-sdk/commit/298fe1da0c7db5515f40e6b97155e6939f401917).


- **Logging:**

    - Fix uvicorn access log formatter to consistently use either human-readable or GELF format.

    - Add logging helpers to optionally hide JWT-like token strings.


## 1.0.4 - 2021-05-26

### Bugfixes

- Fix the initialization of Prometheus metrics exporter endpoint.


- **Logging:**

    - Display uvicorn access log in GELF format.
      
    - Add Gunicorn logging formatter: can be used to export skill logs as GELF-compatible JSON when deploying with Gunicorn.  
    To activate, add [`--logger-class=skill_sdk.log.GunicornLogger`](https://docs.gunicorn.org/en/stable/settings.html#logger-class) parameter when deploying the skill.
  

## 1.0.3 - 2021-05-25

### Features


- Skill Designer UI: a tool for rapid skill prototyping.
    Start a skill with `vs develop [impl]` and hit [http://localhost:4242](http://localhost:4242) 
    to access the UI from a browser.
  

- Support local skill translations in [Rails-compatible](https://guides.rubyonrails.org/i18n.html) YAML format.


## 1.0.2 - 2021-05-05

### Features


- [#49](https://github.com/telekom/voice-skill-sdk/pull/49):
  On-demand debug logging. This feature is activated with `X-User-Debug-Log` header: 
  if header is present in skill invoke request, logging level is lowered to DEBUG.
  

- [#51](https://github.com/telekom/voice-skill-sdk/pull/51):
  Address lookup and device location endpoints of location service:
  
    - `LocationService.device_location` retrieves the device location (the info, a user has set up in companion app) with geo coordinates.

    - `LocationService.address_lookup` returns a list of addresses (with geo-coordinates) for a given query.
    A query consists the address fields (country, zip, street name, house number).

### Bugfixes

- Environment variable placeholders (in `skill.conf`) may now contain curly braces, 
  so you can have formatted string literals as default values.   

## 1.0.1 - 2021-04-08

### Bugfixes

- [#47](https://github.com/telekom/voice-skill-sdk/issues/47):
  Scaffold project files added to both binary and source distribution. 

### Features


- [#45](https://github.com/telekom/voice-skill-sdk/pull/45): 
  New "response_hook" parameter when constructing `requests.Client/AsyncClient`.
  Allows plugging in observability metrics when calling partner services. 
  For example, to count partner service requests with response codes:
  
  ```python
  from skill_sdk.requests import AsyncClient
  from skill_sdk.middleware.prometheus import count_partner_calls
  
  async with AsyncClient(
      response_hook=count_partner_calls("partner-service")
  ) as client:
      response = await client.get("https://partner-service-api")
  ```


- [#43](https://github.com/telekom/voice-skill-sdk/pull/43): 
  Source code documentation has been reviewed. 


- [#42](https://github.com/telekom/voice-skill-sdk/pull/42): 
  Asyncio event loops can be nested when calling `utils.run_until_complete`. 
  Usable when mixing sync and async handlers. 


## 1.0 - 2021-03-26

### Major changes 

#### Explicit concurrency model:
    
Skill SDK for Python supports asynchronous coroutines (`async def` intent handlers):

```python
@skill.intent_handler("HELLO_WORLD__INTENT")
async def handler() -> Response:
  return await long_running_async_function()
```
   
Synchronous handlers are also supported and executed in [ThreadPoolExecutor](https://docs.python.org/3/library/concurrent.futures.html#threadpoolexecutor).


### Breaking changes 

1. No more text services.
   
    This is a major step towards completely phasing out the text services. Only local translations 
    (both gettext `.po/.mo` and YAML formats) are supported. The translations will not be reloaded from cloud service.   
   

2. Global invocation `context` object is replaced with `request` [context variable](https://docs.python.org/3/library/contextvars.html).

    The variable is accessible to intent handlers and is a copy of currently running invoke request: [InvokeSkillRequestDto](https://htmlpreview.github.io/?https://raw.githubusercontent.com/telekom/voice-skill-sdk/blob/master/docs/skill-spi.html#_invokeskillrequestdto).
   

3. Localization became _internationalization_.
	
    `skill_sdk.l10n` is renamed to `skill_sdk.i18n` and [python-babel](http://babel.pocoo.org/en/latest/) is used as translation module.


4. Tracing and Prometheus middleware has become optional.

    To make use of tracings/metrics, skill SDK must be installed with **all** extra: `python -m pip install skill-sdk[all]`.
    With this extra installed, tracing helpers are importable from `skill_sdk.middleware.tracing`, 
    and Prometheus helpers - from `skill_sdk.middleware.prometheus`.


5. Responses are immutable:

    You can create a response (or any related object like Card, Kit, Task, Command) in a constructor.
    After constructing the object, the only way to mutate it is by using the factory methods.
   

### Minor and non-breaking changes 

1. Skill configuration changes.

    Skill configuration is available as attributes of `skill_sdk.config.settings` object.
    For backward compatibility, `skill.conf` file in [ConfigParser](https://docs.python.org/3/library/configparser.html) format is still supported.
    Section names are joined with config keys and converted to upper-case, so that a value `url` in `[service]` section
    is available as `settings.SERVICE_URL`
   
   ```python
   from skill_sdk.config import settings
	
   settings.SKILL_NAME     # skill name - corresponds to **name** attribute in **[skill]** section
   settings.VALUE_FOR_TESTING = "test"  # config values are mutable 
   ```

    It is suggested migrating the skill config to [BaseSetting](https://pydantic-docs.helpmanual.io/usage/settings/) format.  


2. Test helpers have been moved to `skill_sdk.util` module.


3. Python [requests](https://requests.readthedocs.io/en/master/) are replaced with [HTTPX](https://www.python-httpx.org/) client. 
   
    [requests_mock](https://requests-mock.readthedocs.io/) doesn't work any more and is replaced with [respx](https://github.com/lundberg/respx) module. 


4. `requests.CircuitBreakerSession` is deprecated.

    There are now two similar adapters in `skill_sdk.requests`. 
    
    One is `skill_sdk.requests.Client` - an HTTPX synchronous client (`requests.CircuitBreakerSession` is simply an alias for this adapter).
    
    The other is `skill_sdk.requests.AsyncClient` - an asynchronous client compatible with `await`/`async with` statements.

    `good_codes/bad_codes` are replaced with `exclude` parameter.  _Good_ codes are the HTTP status codes between 200 and 399.
    To suppress an exception if HTTP 404 is returned as status code, use `exclude`:
   
    ```python
    from skill_sdk.requests import AsyncClient, codes
   
    with AsyncClient() as client:
        r = await client.request("GET", "my_url", exclude=(codes.NOT_FOUND,))
    ```
