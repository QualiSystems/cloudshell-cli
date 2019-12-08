# CloudShell CLI
[![Build status](https://travis-ci.org/QualiSystems/cloudshell-cli.svg?branch=dev)](https://travis-ci.org/QualiSystems/cloudshell-cli)
[![codecov](https://codecov.io/gh/QualiSystems/cloudshell-cli/branch/dev/graph/badge.svg)](https://codecov.io/gh/QualiSystems/cloudshell-cli)
[![PyPI version](https://badge.fury.io/py/cloudshell-cli.svg)](https://badge.fury.io/py/cloudshell-cli)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

<p align="center">
<img src="https://github.com/QualiSystems/devguide_source/raw/master/logo.png"></img>
</p>

## Overview
The cloudshell-cli open source Python package provides an easy-to-use interface for CLI access and communication (Telnet, TCP, SSH etc.) with network devices.

**Note:** We use tox and pre-commit for testing. For details, see [Services description](https://github.com/QualiSystems/cloudshell-package-repo-template#description-of-services).

## Installation
```bash
pip install cloudshell-cli
```

### Contributing 

We welcome community ideas and contributions, so if you have any feedback or would like to request enhancements, feel free to create an **Issue** in the repository. 

#### Contributing code

1. Fork the repository. 

2. Make the code change. Make sure the tests pass. Add unit tests to cover any new behavior. We do require that the coverage does not decrease with the new code.

3. Submit a **Pull Request**.

## Usage

Cloudshell CLI is highly modular and implements many programming interfaces. 

### Session

**Session** is a service that declares the session parameters, and handles communication with the device. Depending on the communication protocol, you will need to either use **SSHSession** or **TelnetSession**.

To instantiate the session, we need to pass the  parameters:
- **IP address**
- **Username**
- **Password**

For example:

```python
from cloudshell.cli.session.ssh_session import SSHSession


session = SSHSession(host='localhost', username='admin', password='Pass1234')

```

### CommandMode

**CommandMode** enables you to define each mode on your device (in other words, how to enter and leave the mode, and the expected prompt). For example, most network devices include a root (or enable mode) and a configuration mode.

CommandMode uses the following parameters:
**prompt**: (Mandatory) The expected command-line prompt. CLI will 
**enter_command**: (Optional) 
**exit_command**: (Optional)
**parent_mode**: (Optional)

Example - Declaring a single command mode:
```python
from cloudshell.cli.command_mode import CommandMode


mode = CommandMode(prompt='*#', enter_command="configure", exit_command="exit")

```

Example - Declaring two command modes and the hierarchy using `parent_mode`):

```python
from cloudshell.cli.command_mode import CommandMode


enable_mode = CommandMode('*>')
config_mode = CommandMode('*#', enter_command="configure", exit_command="exit", parent_mode=enable_mode)

```

### CLI service
**CLI** is the service that manages the sessions and command modes. 

Now that we've learned how to create the session and declare the command modes, we can start using them, by creating a CLI object and passing the defined session and command modes.

Example - execute 'show interfaces':

```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.command_mode import CommandMode


cli = CLI()
mode = CommandMode(r'my_prompt_regex') # for example r'%\s*$'

session_types = [SSHSession(host='ip_address',username='user_name',password='password')]

with cli.get_session(session_types, mode) as default_session:
    out = default_session.send_command('show interfaces')
    print(out)

```

Note that CLI can switch between the modes automatically. For example, if we have multiple command modes, CLI is able to move back and forth between these modes automatically following the hierarchy defined in the `parent_mode` parameter of each commmand mode. 

To illustrate this point, the following example will execute the first `send_command` in config_mode and then in enable_mode.
First, it will log in to the device and detect the current mode (let's assume it would be enable_mode). Then, it will automatically switch to config_mode by executing the `enter_command` parameter.

Example - using multiple command modes:

```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.command_mode import CommandMode


hostname = "192.168.1.1"
username = "admin"
password = "admin"

enable_mode = CommandMode('*>')
config_mode = CommandMode('*#', enter_command="configure", exit_command="exit", parent_mode=enable_mode)

sessions = [SSHSession(hostname, username, password), TelnetSession(hostname, username, password)]

cli = CLI()

# switch to config mode and send the command:
with cli.get_session(sessions, config_mode) as cli_service:
    output = cli_service.send_command('show interfaces')

# switch to enable mode and send the command:
with cli.get_session(sessions, enable_mode) as cli_service:
    output = cli_service.send_command('show interfaces')

```

## Examples
### Establishing communication with the device

In the following code, we'll create a simple SSH connection to a device. First, we want to import the required packages (lines 51-53), where:



### Switching between configuration modes
In this example, we show how to switch between different modes (enable and configuration) and execute commands in each one.

Notes: 
- We're importing both SSHSession and TelnetSession, so the CLI will try to establish an SSH session and if it can't, will switch to telnet.
- Although we start with config mode in the example, CLI will know that the session starts in enable mode and therefore will run the enable mode part first. To force CLI to follow a specific order, you must use proper indentations.


