
# Changelog
All notable changes to this project will be documented in this file.

## 1.0

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
