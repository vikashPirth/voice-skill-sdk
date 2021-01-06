
# Changelog
All notable changes to this project will be documented in this file.

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
