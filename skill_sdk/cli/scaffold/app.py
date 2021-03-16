#!/usr/bin/env python

from skill_sdk import skill
from impl import hello

app = skill.init_app()

app.include(handler=hello.handler)
