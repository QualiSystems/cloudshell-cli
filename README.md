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

## Key features

CloudShell CLI offers the following key features (For details, see (Usage)[#usage]): 
* Multi-protocol communication, including **SSH** and **Telnet**.
* **Session pool**: CloudShell CLI uses a session pool to store and manage sessions safely between multiple threads using the [Python queue module](https://docs.python.org/3.7/library/queue.html). The maximum session pool size and timeout period are customizable parameters:
  * Maximum session pool size (`max_pool_size`) determines the maximum number of concurrent sessions in the session pool (default is 1).
  * Timeout period (`pool_timeout`) determines the maximum time a thread can wait for a session (default is 100 seconds).
* **cli service** allows CloudShell CLI to switch between the device's CLI modes.

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

CloudShell CLI is highly modular and implements many programming interfaces. 

### Session

**Session** is a service that initializes the session by declaring the session parameters and handles communication with the device. Depending on the communication protocol, you will need to either use **SSHSession** or **TelnetSession**.

_**Note:** Creating a session object does not create a connection to the device. This is done by `SessionPoolManager` as part of the CLI's `get_session` command. Once the connection is established, the new session is stored and managed by the `SessionPoolManager`._ 

To initialize the session, we need to pass the  parameters:
- **IP address**
- **Username**
- **Password**

**Example: Initializing the session**

```python
from cloudshell.cli.session.ssh_session import SSHSession


session = SSHSession(host='localhost', username='admin', password='Pass1234')
```

### CommandMode

**CommandMode** enables you to define each mode on your device (in other words, how to enter and leave the mode, and the expected prompt). For example, most network devices include a root (or enable mode) and a configuration mode.

CommandMode uses the following basic parameters:
* **prompt**: (Mandatory) The expected command-line prompt. CLI will 
* **enter_command**: (Optional) The CLI command to execute in order to enter a certain mode. For example, to enter config mode in Cisco, you need to run something like: 
```bash
nexus#
nexus# configure terminal
nexus(config)#
```
* **exit_command**: (Optional) The command to execute in order to exit a certain mode.
* **parent_mode**: (Optional) Parameter that defines the preceding CLI mode.

_**Note:** You're welcome to check the CommandMode docstring for additional parameters._

**Example - Declaring a single command mode:**
```python
from cloudshell.cli.command_mode import CommandMode


mode = CommandMode(prompt='*#')

```

**Example - Declaring two command modes and the hierarchy using `parent_mode`):**

```python
from cloudshell.cli.command_mode import CommandMode


enable_mode = CommandMode('*>')
config_mode = CommandMode('*#', enter_command="configure terminal", exit_command="exit", parent_mode=enable_mode)

```

### CLI service
**cli service** is the service that manages the sessions and command modes and allows us to send commands to the device and switch between the modes automatically. For example, if we have multiple command modes, cli service is able to move back and forth between these modes following the hierarchy defined by the `parent_mode` parameter of each commmand mode.  

**Example - Executing 'show interfaces'**

Now that we've learned how to define the session and declare the command modes, we can start using them by creating a CLI object and passing the defined session and command modes.

```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.command_mode import CommandMode


cli = CLI()
mode = CommandMode(r'my_prompt_regex') # for example r'%\s*$'

session_types = [SSHSession(host='ip_address',username='user_name',password='password')]

with cli.get_session(session_types, mode) as cli_service:
    out = cli_service.send_command('show interfaces')
    print(out)

```

**Example - Providing different communication protocols**

In the previous example, we assumed the device works over SSH. However, you can specify multiple communication protocols (for example, SSH and Telnet). In such a case, CloudShell will attempt connection with each provided protocol until it finds the one that works.

```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.session.telnet_session import TelnetSession
from cloudshell.cli.command_mode import CommandMode


cli = CLI()
mode = CommandMode(r'my_prompt_regex') # for example r'%\s*$'

session_types = [SSHSession(host='ip_address',username='user_name',password='password')]

with cli.get_session(session_types, mode) as cli_service:
    out = cli_service.send_command('show interfaces')
    print(out)

```
**Example - Using multiple command modes**

To illustrate this point, the following example will execute a `show interfaces` in config_mode and then `show version` in enable_mode.
First, CloudShell CLI will get a session to the device from the session pool (which will create a new one if empty). The cli service will use the session to access the device and detect the current mode (let's assume it's **enable_mode**). Then, it will automatically switch to config_mode by executing the `enter_command` parameter, as specified in the **config_mode**'s definition.

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

#----------------------------------------------------------
# switch to config mode and send the command:
with cli.get_session(sessions, config_mode) as cli_service:
    output = cli_service.send_command('show interfaces')

# switch to enable mode and send the command:
with cli.get_session(sessions, enable_mode) as cli_service:
    output = cli_service.send_command('show version')
#----------------------------------------------------------
# OR switch between the modes by enter_mode command:
#----------------------------------------------------------
with cli.get_session(sessions, enable_mode) as cli_service:
    output = cli_service.send_command('show version')
    with cli_service.enter_mode(config_mode) as config_cli_service:
        print(config_cli_service.send_command('show interfaces'))
        output = config_cli_service.send_command('show configuration')
#----------------------------------------------------------

```

**Example - Switching back to the previous mode**

In the previous example, we learned how to switch from enable_mode to config_mode and send commands in each. Now let's say you're in config_mode and want to return to enable_mode. To do so, simply return to the enable_mode block's indentation and specify your command. 

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

with cli.get_session(sessions, enable_mode) as cli_service:
    output = cli_service.send_command('show version')
    with cli_service.enter_mode(config_mode) as config_cli_service:
        print(config_cli_service.send_command('show interfaces'))
        output = config_cli_service.send_command('show configuration')
    # switch back to enable_mode and send a command
    cli_service.send_command("some command")
    
```

As is the case with Python, switching back to the previous command mode closes the current `with` statement (config_mode in our case), so returning to config_mode would require specifying another `with` statement with the proper indentation.



