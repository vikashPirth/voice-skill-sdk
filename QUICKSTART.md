# Magenta Voice Skill SDK for Python

# Quickstart

Make sure to have an actual version of <a href="https://docs.python.org/3/">**Python 3**</a> (3.7 is minimum required)
and <a href="https://pip.pypa.io/en/stable/">**pip**</a>:
`apt-get install python3-pip` if you don't or `brew install python3` if you're on MacOS.

> _Note:_ Some distros might require `python3-venv` package installed.
> Run `apt-get install python3-venv` if you encounter difficulties when creating virtual environments for new projects. 

1. Clone the repo: `https://github.com/telekom/voice-skill-sdk.git`
2. Change to SDK dir: `cd voice-skill-sdk`
3. Run *new-skill* install:  `python setup.py new_skill`

> Alternatively, a one-liner for [@4thel00z](https://github.com/4thel00z)
>
> `pip download --no-deps --no-binary :all: skill_sdk && tar xzf skill-sdk-*.tar.gz && python skill-sdk-*/setup.py new_skill`
>


You'll be prompted for:
- The skill name. Give it an Awesome Name! 
- Programming language. Python is Awesome!
- The directory where the project will be created. Make sure it's writable. 

This script will:
- Create a new project in the directory of your choice.
- Add a virtual environment to `.venv` inside your project.
- Install required dependencies.
 
You may now open your skill directory as a project in PyCharm. 

> If you get an error `This package requires Python version >= 3.7 and Python's setuptools`, you happen to have an outdated Python version.
> Check it with `python --version` and make sure it is >= 3.7

*Happy coding!*

# Further reading:
- Please check the [installation guide](docs/install.md) for technical details.
- You can find the docs here: [Python SDK Documentation](docs/README.md) 
- Have a look at the [Contribution Guide](CONTRIBUTING.md)
- [Working with Demo Skill](docs/articles/demo_skill.md)
- [Creating a Custom Weather Skill](docs/articles/weather_skill.md)

Requires Python 3.7! [Type hints](https://docs.python.org/3/library/typing.html) FTW!
* [PEP 526: Syntax for variable annotations](https://docs.python.org/3.6/whatsnew/3.6.html#whatsnew36-pep526)
* [PEP 484: Type Hints](https://docs.python.org/3.5/whatsnew/3.5.html#whatsnew-pep-484)

# Remark:
This repository uses the `*_test.py` naming schema. PyCharm discovers everything automatically. But if you like to invoke unit tests from the command line, and you are not sure about how, please check `scripts/test`.
