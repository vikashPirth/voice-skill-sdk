# Introduction

Magenta Skill SDK for Python is a Python package that assists in creating skill implementations for Magenta Smart Ppeaker in Python.

It contains 

- a set of Python modules that will create a microservice serving the skill, 
- a wrapper that abstracts the HTTP calls into Python function call, 
- some helpful libraries, 
- a few scripts and 
- other useful contributions.

Skill SDK for Python handles the [Skill SPI](https://htmlpreview.github.io/?https://raw.githubusercontent.com/telekom/voice-skill-sdk/master/docs/spi/index.html) (Service Provider Interface).  
The SPI defines the communication between CVI core and the skills.  
This SPI is maintained by the CVI core developers and represents the current interface between the CVI core and the skills.

**Further information**

- [Skill SPI Documentation](spi/index.html)
- [Changelog](spi/CHANGELOG.md)
- Example requests/responses as JSON files:
    * [Skill info - SkillInfoResponseDto](spi/SkillInfoResponseDto.json)
    * [Skill invoke - InvokeSkillRequestDto](spi/InvokeSkillRequestDto.json)
    * [Skill response - InvokeSkillResponseDto](spi/InvokeSkillResponseDto.json)

