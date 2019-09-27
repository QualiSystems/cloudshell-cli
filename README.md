# cloudshell-cli
[![Build status](https://travis-ci.org/QualiSystems/cloudshell-cli.svg?branch=dev)](https://travis-ci.org/QualiSystems/cloudshell-cli)
[![codecov](https://codecov.io/gh/QualiSystems/cloudshell-cli/branch/dev/graph/badge.svg)](https://codecov.io/gh/QualiSystems/cloudshell-cli)
[![PyPI version](https://badge.fury.io/py/cloudshell-cli.svg)](https://badge.fury.io/py/cloudshell-cli)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/python/black)

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

class CreateSessionSimpleCase():

    def create_my_session(self):

        cli = CLI()
        mode = CommandMode(r'my_prompt_regex') # for example r'%\s*$'

        session_types = [SSHSession(host='ip_address',username='user_name',password='password')]


        with cli.get_session(session_types, mode) as default_session:
            out = default_session.send_command('my command')
            print(out)

```
###Description:

In the above code we create a simple SSH connection to our device. We first import the required packages (lines 51-53), where:
- CLI is an API providing access for creating the new session into the device. 
- SSHSession is an API providing functions to declare the session parametrs, as well as functions to connect and dis-connect from the session. Note that you can create you're own session class similar to SSHSession structure.
- CommandMode is an API providing you the ability to define each mode on your device. For example on switches there may be several modes as configuration mode, admin mode. So using the CommandMode interface you able to define how to enter each mode, how to leave mode, what is the expected prompt.

## Advanced CLI usage (level I):
```python
from cloudshell.cli.cli import CLI
from cloudshell.cli.session.ssh_session import SSHSession
from cloudshell.cli.command_mode import CommandMode

class CreateSessionAdvancedCase():
    def create_my_session(self):
        cli = CLI()
        mode = CommandMode(r'my_prompt_regex')
        session_types = [SSHSession(host='ip_address',username='user_name',password='password')]
        with cli.get_session(session_types, mode) as default_session:
            out = default_session.send_command('my command')
            print(out)
            config_command_mode = CommandMode(r'my_config_prompt_regex')
            with default_session.enter_mode(config_command_mode) as config_session:
                out = config_session.send_command('my config mode command')
                print(out)
```
## CLI Usage for Cloudshell users
In this case we must to get all the data about our device and session from the resource configured on cloudshell. For this porpuse we will use the context object receiving from cloudshell. 
For the sake of our example, we will define the context object here and just use it with our example.
```python
def create_context():
    from cloudshell.shell.core.context import ResourceCommandContext, ResourceContextDetails, ReservationContextDetails
    context = ResourceCommandContext()
    context.resource = ResourceContextDetails()
    context.resource.name = 'CiscoIOS'
    context.reservation = ReservationContextDetails()
    context.reservation.reservation_id = '5695cf87-a4f3-4447-a08a-1a99a936010e'
    context.reservation.owner_user = 'admin'
    context.reservation.owner_email = 'fake@qualisystems.com'
    context.reservation.environment_path ='Environment-Exmaple'
    context.reservation.environment_name = 'Environment-Exmaple'
    context.reservation.domain = 'Global'
    context.resource.attributes = {}
    context.resource.attributes['CLI Connection Type'] = 'SSH'
    context.resource.attributes['User'] = 'cisco_user'
    context.resource.attributes['AdminUser'] = 'cisco_admin_user'
    context.resource.attributes['Console Password'] = '3M3u7nkDzxWb0aJ/IZYeWw=='
    context.resource.attributes['Password'] = 'PgkOScppedeEbHGHdzpnrw=='
    context.resource.attributes['Enable Password'] = 'PgkOScppedeEbHGHdzpnrw=='
    context.resource.address = '192.168.1.2'
    context.resource.attributes['SNMP Version'] = '2'
    context.resource.attributes['SNMP Read Community'] = 'Test1234'
    context.resource.attributes['Model'] = 'Enterprises.2011.2.23.339'
    context.resource.attributes['AdminPassword'] ='DxTbqlSgAVPmrDLlHvJrsA=='
    context.resource.attributes['Vendor'] = 'Cisco'
    return context
```

Next we will explain how to define modes for the session. For example in routers there may be a default mode, a configuration mode an admin mode etc.
In the mode object we can define expected_map, which is used in cases when we expect to questions from the cli we specify the required response. We can also define error_map to catch run time errors on the switch.

First we wiil define a default actions class 
```python
class DefaultActions(object):
    def __init__(self):
        pass
    def actions(self, session, logger):
        out = session.hardware_expect('echo default' , DefaultCommandMode.PROMPT,
                                      logger,action_map={r'%\s*$': lambda session, logger: session.send_line('cli', logger)})
```

With the DefaultActions class we define all the commands we need to initiate the console on the session. For example on a switch a default action can be "set cli screen-length 0" to print all in once to the screen.
actions function is the functon that invokes TODO

We use tox and pre-commit for testing. [Services description](https://github.com/QualiSystems/cloudshell-package-repo-template#description-of-services)
