
# Changelog
All notable changes to this project will be documented in this file.

## [v0.16.0] - 2021-12-07    

### Features
-  Add a new ReferenceType called MEDIA_CONTENT_END. 

## [v0.15.3] - 2021-08-05   

### Bugfixes

-   Fixed "X-Tenant-Id"/"Baggage-X-Magenta-Transaction-Id" tracing headers propagation and logging. 

## [v0.15.2] - 2021-07-26    

**Features**

-   Magenta transaction Id value added to logging record.
-   "Tenant" logging value is read from "X-TenantId" header.
    >**IMPORTANT**: for logging purpose only, do not use this header to build tenant-specific logic.    


**Miscellaneous**

-   Requirements bump:
    - apispec from 4.6.0 to 4.7.1
    - python-dateutil from 2.8.1 to 2.8.2
    - requests from 2.25.1 to 2.26.0


## [v0.15.1] - 2021-07-12    

**Features**

-   Support "Baggage-X-Magenta-Transaction-Id" tracing header propagation. 
>   **Note:** this header is not supported by [B3-codec](https://github.com/openzipkin/b3-propagation), 
>   and will be dropped, if zipkin tracer client activated.

## [v0.15.0] - 2021-06-22    

**Features**

-   Added support for a new companion app cards format: Action Cards v3.0.


**Miscellaneous**

-   Requirements bump:
    - apispec from 4.5.0 to 4.6.0


## [v0.14.4] - 2021-06-10  

**Bugfixes**

-   Fixed `skill.test_intent` helper FALLBACK_INTENT handling. 

**Miscellaneous**

-   Requirements bump:
    - apispec from 4.4.0 to 4.5.0
    - prometheus_client from 0.10.0 to 0.11.0

## [v0.14.3] - 2021-05-12  

**Features**

-   Internationalization module supports YAML translations in [RoR i18n](docs/i18n.md#Ruby on Rails i18n Translations) format.  

**Bugfixes**

-   Test helper `skill.test_intent` fixed with correct intent name creating a test invoke context. 

## [v0.14.2] - 2021-05-05  

**Bugfixes**

-   Environment variable placeholders can contain curly braces in default values. 
    You can define formatted string literals as default values.   


-   Location service returns 404 (Not Found) if no location data is present for a device. 
    This error code is now treated as normal, and `None` value is returned instead. 

## [v0.14.1] - 2021-05-04  

**Features**

-   Device location endpoint added to location service. 
    It is a preferable way for a skill to get device location information, such as address or zip-code.  

**Miscellaneous**

-   Requirements bump:
    - apispec from 4.3.0 to 4.4.0
    - arrow from 1.0.2 to 1.1.0
    - gunicorn from 20.0.4 to 20.1.0
    - prometheus_client from 0.10.0 to 0.10.1
    - py-zipkin from 0.20.1 to 0.20.2 
    - requests-mock from 1.8.0 to 1.9.2


## [v0.14.0] - 2021-03-22  

**Miscellaneous**

-   Skill SPI has been bumped to version 1.4.1.
    
    You can now attach [client tasks](docs/client_tasks.md) to the response, for example, 
    tell the client to execute another intent:
    ```python
    import datetime
    from skill_sdk.responses import ClientTask, Response
    
    response = Response("Weather forecast follows.").with_task(
        ClientTask.invoke("WEATHER__INTENT")
    )
    ```


## [v0.12.2] - 2021-03-12  

**Bugfixes**

-   Translation reload worker has been fixed. 

## [v0.12.1] - 2021-03-12  

**Features**

-   `X-Testing`/`Testing` headers forwarding: these headers are used to distinguish test traffic.
    To propagate the headers, set `internal` flag when creating a circuit breaker for HTTP requests session:
    
    ```python
    from skill_sdk.requests import CircuitBreakerSession
    
    with CircuitBreakerSession(internal=True) as session:
        result = session.get("https://internal-service.local")
    ```


## [v0.12.0] - 2021-03-02  

**Features**

-   Multi-string translations support in YAML format. <br />
    You can download the translations from text service and save as YAML in your skill project:
    `python manage.py translate [modules...] --format yaml --download-url TEXT_SERVICE_URL --token AUTH_TOKEN --tenant GLOBAL`<br />
    YAML translations will take precedence over [gettext](https://www.gnu.org/software/gettext/). 
    `{lang}.po/{lang}.mo` translations are ignored if `{lang}.yaml` found.    


**Miscellaneous**

- [arrow](https://pypi.org/project/arrow/) dependency became optional and moved to "requirements-dev.txt".<br/>
    **IMPORTANT**: if your skill uses [arrow](https://pypi.org/project/arrow/), add this requirement explicitly.


-   Requirements bump:
    - arrow from 0.17.0 to 1.0.2 
    - coverage from 5.4 to 5.5


## [v0.11.1] - 2021-02-25  

**Features**

-   Add `l10n.Message.join` to simplify joining list elements. 

## [v0.11.0] - 2021-02-18  

**Bugfixes**

-   Session size limit check has been removed.

**Miscellaneous**

-   Skill SPI has been bumped to version 1.3. 
-   Requirements bump:
    - apispec from 4.2.0 to 4.3.0 

## [v0.10.5] - 2021-02-10  

**Features**

-   Multi Date Handling in Entities: helper methods to filter list of dates e.g. using the tense used by the user question to get a past or future date. "What date was Monday" vs. "What date is Monday" 


**Miscellaneous**

- Due to the security issue with its underlying dependency [Tornado](https://pypi.org/project/tornado/), 
  [jaeger-client](https://pypi.org/project/jaeger-client/) became an optional dependency.   
  

- Test/development requirements moved to "requirements-dev.txt".<br />
    **IMPORTANT**: if your skill uses [coverage](https://pypi.org/project/coverage/) 
  or [requests-mock](https://pypi.org/project/requests-mock/) to run unit tests, you would have to 
  explicitly install those before: `pip install coverage requests-mock` 
  

- Requirements bump:
    - apispec from 4.0.0 to 4.2.0 
    - gevent from 20.12.1 to 21.1.2 
    - pyyaml from 5.3.1 to 5.4.1  
    - timezonefinder from 5.0.0 to 5.2.0
    - coverage from 5.3.1 to 5.4

## [v0.10.4] - 2021-01-19  

**Features**

-   `skill->debug` [config option](docs/config.md#skill) is introduced. 
    Skill running with _debug_ **on** returns exception details and traceback in a response. 
    Starting the skill in development mode activates the _debug_ flag.    

**Bugfixes**

-   Add `skill_genedrator` package to the source distribution.
    
-   Remove `__add__/__radd__` magic from "l10n.Message" as confusing.

**Miscellaneous**

-   Rewrite [installation guide](docs/install.md).

-   Log debug messages when running `install/new_skill` commands (suppress with standard `--quiet (-q)`) parameter.


## [v0.10.3] - 2021-01-13  

**Bugfixes**

- Disable `l10n.Message` dictionary serialization in response.  
  
## [v0.10.2] - 2021-01-06  

**Bugfixes**

- Development/production requirements merged for backward compatibility with existing CI/CD pipelines.  
  
## [v0.10.1] - 2021-01-04  

**Miscellaneous**

- Swagger UI is updated to v3.38.0 
  
- Requirements bump:
    - coverage from 5.3 to 5.3.1
    - gevent from 20.9.0 to 20.12.1
    - opentracing from 2.3.0 to 2.4.0  
    - requests from 2.25.0 to 2.25.1

## [v0.10.0] - 2020-12-18  

**Features**

-   Client kits and actions API added to the responses.

**Bugfixes**

-   Log an error if device timezone is missing or invalid in intent context.
    Sample configuration added to [context.md](docs/context.md). 

-   Fix card attribute names conversion from snake_case to camelCase.

**Miscellaneous**

-   Skill SPI has been bumped to version 1.2. 

## [v0.9.2] - 2020-11-27  

**Bugfixes**

-   Add Pycharm project and run-time configurations to skill template.


## [v0.9.1] - 2020-11-24  

**Bugfixes**

-   Thread-local request leak closed.


## [v0.9.0] - 2020-11-13 

Initial release
