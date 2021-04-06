#!/usr/bin/env python

"""Your application instance"""

from skill_sdk import skill
from impl import hello

# Create a skill instance
app = skill.init_app()

# Add "SMALLTALK__GREETINGS" intent handler
app.include(handler=hello.handler)
