__author__ = 'ini'
import time

def send_username(session, retry):
    """
        Sending username to device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """
    session.sendline(session._username)
    time.sleep(1)

def send_password(session, retry):
    """
        Sending password to device

        :param session:
        :param retry:
        :return:
    """
    session.sendline(session._password)
    time.sleep(1)

def send_default_password(session, retry):
    """
        Sending default password to device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """

    session.sendline(session._enable_password)

def send_empty_string(session, retry):
    """
        Sending empty string to device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """

    logger = session.get_logger()
    logger.info('Send empty')
    session.sendline('')

def do_reconnect(session, retry):
    """
        Reconecting to the device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """
    session.reconnect()

def send_yes(session, retry):
    """
        Sending 'yes' to device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """
    if retry < 5:
        session.sendline('yes')
    else:
        session.sendline('')

def wait_prompt_or_reconnect(session, retry):
    """
        Wait prompt and if it not in buffer then reconnect

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """
    logger = session.get_logger()
    if retry < 3:
        session.sendline('')
        logger.error('Timeout while getting prompt. Wait 5 seconds and retry.')
        time.sleep(5)
    elif 2 < retry < 5:
        logger.info('Timeout while getting prompt on device, sending Ctrl+C ...')
        session.sendcontrol('c')
        logger.info('Wait 10 seconds and retry to get prompt')
        time.sleep(10)
    else:
        session.reconnect()

def send_command(session, retry):
    """
        Sending command to device

        :param session: handler for sending data
        :param retry: count of retries
        :return:
    """
    session.sendline(session.command)
