
# Changelog
All notable changes to this project will be documented in this file.

## Unreleased


### Bugfixes

- **Logging:**

    - Fix uvicorn access log formatter to consistently use either human-readable or GELF format.

    - Add logging helpers to possibly hide JWT-like token strings.


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
