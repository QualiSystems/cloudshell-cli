from cloudshell.cli.session_handler import SessionHandler

class SessionModeWrapper(object):

    def __init__(self, session, connection_manager,default_command_mode):

        self._session = session
        self._command_mode = default_command_mode
        self.connection_manager = connection_manager

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        print '__exit__()'


    def set_current_mode_for_session(self,curr_mode):
        self._command_mode = curr_mode

    def get_current_mode_for_session(self):
        return self._command_mode


    def pop_session_from_pool(self,connection_manager):
        '''
        this function made to remove the session from the pool such that another process will not use and change it in parallel
        :param connection_manager:
        :return:
        '''
        session = connection_manager.get_session_instance()
        return session

    def push_session_to_pool(self,session):
        self.connection_manager.return_session_instance(session)


    def change_mode(self, command_mode):
        return command_mode


    def send_command(self, command, expected_string=None, command_mode=None, logger=None, *args, **kwargs):
        if command_mode:
            self._command_mode = self.change_mode(command_mode)

        if not expected_string:
            expected_string = self._command_mode.promt

        self._session.logger = logger
        self._session.hardware_expect(command, expected_string=expected_string, *args, **kwargs)


