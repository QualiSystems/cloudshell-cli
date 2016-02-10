__author__ = 'ini'
import time


def sendUsername(session, retry):
    session.sendline(session._username)
    time.sleep(1)

def sendPassword(session, retry):
    session.sendline(session._password)
    time.sleep(1)

def sendDefaultPassword(session, retry):
    session.sendline(session._enable_password)

def sendEmptyString(session, retry):
    logger = session.getLogger()
    logger.info('Send empty')
    session.sendline('')

def doReconnect(session, retry):
    session.reconnect()

def sendYes(session, retry):
    if retry < 5:
        session.sendline('yes')
    else:
        session.sendline('')

def waitPromptOrReconnect(session, retry):
    logger = session.getLogger()
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


def sendCommand(session, retry):
    session.sendline(session.command)
