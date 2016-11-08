# cloudshell-cli
![alt tag](https://travis-ci.org/QualiSystems/cloudshell-cli.svg?branch=7.0_refactoring)
[![Coverage Status](https://coveralls.io/repos/github/QualiSystems/cloudshell-cli/badge.svg?branch=dev)](https://coveralls.io/github/QualiSystems/cloudshell-cli?branch=dev)
[![PyPI version](https://badge.fury.io/py/cloudshell-cli.svg)](https://badge.fury.io/py/cloudshell-cli)
[![Dependency Status](https://dependencyci.com/github/QualiSystems/cloudshell-cli/badge)](https://dependencyci.com/github/QualiSystems/cloudshell-cli)
[![Stories in Ready](https://badge.waffle.io/QualiSystems/cloudshell-cli.svg?label=ready&title=Ready)](http://waffle.io/QualiSystems/cloudshell-cli)

<p align="center">
<img src="https://github.com/QualiSystems/devguide_source/raw/master/logo.png"></img>
</p>

# CloudShell CLI
A Python package providing an easy abstraction interface for CLI access and communication (Telnet, TCP, SSH etc.) for network devices.

# Download
You can download a free version of CLI here. 

# Installation
CLI is available on PyPy, you can install it by invoking pip command _pip install cloudshell-cli_

## Contributing 

We welcome community ideas and contributions. 

To provide feedback or request enhancements simply create an issue in the repository. 
You can use the [Waffle Board](https://waffle.io/QualiSystems/cloudshell-cli) to add issues directly and catch up on the current backlog progress.

### Contributing code

1. Fork the repository. 

2. Make the code change. Make sure the tests pass. Add unit tests to cover any new behavior. We do require that the coverage does not decrease with the new code.

3. Submit a PR 

### Running the tests

This repository uses nose to run tests. To run all tests run the following from command line:

```Bash
nosetests
```

# Examples
-------------------------------------------------------------------------------------------------------------------

Cloudshell CLI is highly modular and implements many programming interfaces. There is an usage of simple CLI commnads as well as an advanced usage for more complicated behaviours. 

## Simple CLI usage:
```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.command_mode import CommandMode

class CreateSessionSimpleCase(unittest.TestCase):

    def create_my_session(self):

        cli = CLI()
        mode = CommandMode(r'%\s*$')

        session_types = [SSHSession(host='ip_address',username='user_name',password='password')]


        with cli.get_session(session_types, mode) as default_session:
            out = default_session.send_command('my command')
            print(out)

```
###Description:

The above code
