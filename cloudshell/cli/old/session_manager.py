__author__ = 'g8y3e'

from abc import ABCMeta, abstractmethod
import time
import re
import sys
import socket

from cloudshell.cli.old.helpers import normalize_buffer



class SessionManager:
    TIMEOUT_ERR = 'timeout'
    __metaclass__ = ABCMeta

    def __init__(self, handler=None, username=None, password=None, host=None, port=None,
                 timeout=60, newline='\r', logger=None, **kwargs):
        self._handler = handler
        self._logger = logger
        self._host = host
        self._port = port
        self._username = username
        self._password = password

        self._enable_password = password
        if 'enable_password' in kwargs:
            self._enable_password = kwargs['enable_password']

        self._newline = newline
        self._timeout = timeout
        self._current_send_string = ''
        if 'display' in kwargs.keys():
            self._display = kwargs['display']
        else:
            self._display = False
        self.command = ''

        self._is_unsafe_mode = False

    def __del__(self):
        self.disconnect()

    def get_host(self):
        """
            Get host of current device

            :return: str
        """
        return self._host

    def turn_on_display(self):
        """
            Turn on display

            :return:
        """
        self._display = True

    @abstractmethod
    def connect(self, expected_str=''):
        """
            Connecting to device

            :param expected_str: regular expressin strng
            :return:
        """
        pass

    @abstractmethod
    def disconnect(self):
        """
            Disconnect from device

            :return:
        """
        pass

    def _read_start_up_buffer(self, expected_str, timeout):
        """
            Read buffer on session begin

            :param expected_str: regular expression string
            :param timeout: time for waiting buffer
            :return: str
        """
        output = self.expect(expected_str, timeout)
        self._logger.info(output)
        if output == -1:
            output = self.hardware_expect('', expected_str, timeout)

        return output

    def set_unsafe_mode(self, state):
        """
            Setting unsafe mode

            :param state: unsafe bool
            :return:
        """
        self._is_unsafe_mode = state

    def _send(self, command_string):
        """
            Send data to device

            :param command_string: command string
            :return:
        """
        pass

    def _receive(self, timeout=None):
        """
            Read data from device

            :param timeout: time for waiting buffer
            :return:
        """
        pass

    def get_logger(self):
        """
            Get curretn logger
            :return: QSLogger
        """
        return self._logger

    def get_handler(self):
        """
            Get current session handler

            :return:SessionManager
        """
        return self._handler

    def send_line(self, send_string):
        """
            Saves and sends the send string provided

            :param send_string:
            :return: void
        """
        self._current_send_string = send_string
        self._send(self._current_send_string + self._newline)

    def reconnect(self, prompt=None, retries_count=5, sleep_time=15):
        """
            Reconnect to device

            :param prompt: regular expression string
            :param retries_count: count of retries for read data from device
            :param sleep_time: time sleeping between reading buffer
            :return:
        """
        self._logger.info("Reconnect, retries: {0}, sleep_time: {1}".format(retries_count, sleep_time))
        for retry in range(retries_count):
            try:
                self.disconnect()
                self.connect(prompt)
                return

            except Exception as e:
                self._logger.error(e)
                time.sleep(sleep_time)

        raise Exception('Session Manager', "Can't connect!")

    def hardware_expect(self, cmd, expected_str, timeout=30, expected_map={}, retry_count=10):
        """
            Send 'enter' character to remote session and expect to get prompt
            send command and expect for prompt aggregate output buffer and return it.

            :param cmd: - command to send
            :param expected_str: - expect for specific string in session output (optional, default is self._prompt)
            :param timeout: - timeout for expect (optional)
            :param expected_map: - map of patterns and actions to do
            :return: out - channel output after command sent
        """

        if len(expected_map) == 0 and expected_str is None:
            raise Exception('Session Manager', 'Expect string is None!')

        out = ''
        self.command = cmd
        command_sent = False
        self._timeout = timeout

        expected_list = ['[Ii]nvalid\s+[Ll]ogin|[Ll]ogin\s+(incorrect|[Ii]nvalid)', '[Pp]assword:', '[Tt]imeout', '[Ll]ogin.*:|[Uu]ser.*:', expected_str]
        if not expected_map is None:
            expected_list += expected_map.keys()

        if self._is_unsafe_mode or len(self.command) == 0:
            self.send_line(self.command)
            command_sent = True
        else:
            self.send_line('\n')

        for retry in range(retry_count):
            expected_out = self.expect(expected_list, self._timeout)
            self._logger.info(expected_out[1])

            if expected_out != -1:
                i = expected_out[0]
                out += expected_out[1]

                if i == 0:
                    # got invalid send enter to retry
                    if retry < 7:
                        self.send_line('')
                    else:
                        raise Exception('Session Manager', 'Failed to login with provided credentials.')

                elif i == 1:
                    #send password
                    self.send_line(self._password)
                    time.sleep(1)
                elif i == 2:
                    # got timeout send enter to retry
                    self.send_line('')
                elif i == 3:
                    #send Username
                    self.send_line(self._username)
                    time.sleep(1)
                elif i == 4:
                    #for expected_str
                    if command_sent:
                        break
                    else:
                        self.send_line(cmd)
                        command_sent = True
                else:
                    expected_map[expected_list[i]](self, retry)
            else:
                time.sleep(0.1)

        return out

    def expect(self, re_strings='', timeout=None):
        """
            This function takes in a regular expression (or regular expressions)
            that represent the last line of output from the server.  The function
            waits for one or more of the terms to be matched.  The regexes are
            matched using expression \n<regex>$ so you'll need to provide an
            easygoing regex such as '.*server.*' if you wish to have a fuzzy match.
            Keyword arguments:
            re_strings -- Either a regex string or list of regex strings that
                          we should expect.  If this is not specified, then
                          EOF is expected (i.e. the shell is completely closed
                          after the exit command is issued)
            timeout -- Timeout in seconds.  If this timeout is exceeded, then an
                       exception is raised.
            Returns:
            - EOF: Returns -1
            - Regex String: When matched, returns 0
            - List of Regex Strings: Returns the index of the matched string as
                                     an integer
            Raises:
                exception on timeout
        """
        if re_strings is None:
            raise Exception('Session Manager', 'Expect string is None!')

        # Create an empty output buffer
        current_output = ''
        try:
            current_output = self._receive(timeout)
        except socket.timeout as err:
            return -1
        except Exception as err:
            raise err

        # This function needs all regular expressions to be in the form of a
        # list, so if the user provided a string, let's convert it to a 1
        # item list.
        if len(re_strings) != 0 and isinstance(re_strings, str):
            re_strings = [re_strings]

        # Loop until one of the expressions is matched or loop forever if
        # nothing is expected (usually used for exit)

        while (not len(re_strings) == 0):
            res = None
            for re_string in re_strings:
                res = re.search(re_string, current_output, re.DOTALL)
                if res:
                    break
            if res:
                break
            else:
                time.sleep(0.2)

            # Read some of the output
            try:
                buffer = self._receive(timeout)
            except socket.timeout as err:
                return -1
            except Exception as err:
                raise err

            # If we have an empty buffer, then the SSH session has been closed
            if len(buffer) == 0:
                break

            # Strip all ugly \r (Ctrl-M making) characters from the current
            # read
            buffer = buffer.replace('\r', '')

            # Display the current buffer in realtime if requested to do so
            # (good for debugging purposes)
            if self._display:
                sys.stdout.write(buffer)
                sys.stdout.flush()

            # Add the currently read buffer to the output
            current_output += buffer

        # Grab the first pattern that was matched
        if len(re_strings) != 0:
            found_pattern = [(re_index, re_string)
                             for re_index, re_string in enumerate(re_strings)
                             if re.search('.*' + re_string,
                                          current_output, re.DOTALL)]

        # Clean the output up by removing the expect output from the end if
        # requested and save the details of the matched pattern
        if not len(re_strings) == 0 and not len(found_pattern) == 0 and \
                not found_pattern is None:

            return [found_pattern[0][0], normalize_buffer(current_output)]
        else:
            # We would socket timeout before getting here, but for good
            # measure, let's send back a -1
            return [-1, normalize_buffer(current_output)]

    def get_username(self):
        """
            Get current username
            :return: str
        """
        return self._username

    def get_password(self):
        """
            Get current password
            :return: str
        """
        return self._password
