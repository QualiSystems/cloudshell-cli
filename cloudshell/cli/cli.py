from logging import Logger                            


class Cli(object):
    SSH = 'ssh'
    TELNET = 'telnet'
    TCP = 'tcp'

    def change_mode(self, command_mode):
        return command_mode

    def send_command(self, command, expected_string=None, command_mode=None, logger=None, *args, **kwargs):
        if command_mode:
            self._command_mode = self.change_mode(command_mode)

        if not expected_string:
            expected_string = self._command_mode.promt

        self._session.logger = logger
        self._session.hardware_expect(command, expected_string=expected_string, *args, **kwargs)


    # self.session = None
    # self.logger = Logger('logger')
    # self.cli_service = CliService(None)
    # self.initiate_connection_obj = True
    # self.initiate_actions = None
    # self._logger = None
    # self.session_manager = None



    def _get_session_type(self,argument):
        session_types = {
            'ssh': __import__('cloudshell.cli.session.ssh_session', fromlist=[_sessions_map['ssh']]),
            'telnet': __import__('cloudshell.cli.session.tcp_session', fromlist=[_sessions_map['telnet']]),
            'tcp': __import__('cloudshell.cli.session.telnet_session', fromlist=[_sessions_map['tcp']])
        }
        func = session_types.get(argument, lambda: "auto")
        if (argument in _sessions_map):
            return getattr(func, _sessions_map.get(argument))
        else:
            return None

    def new_session(self,session_type,ip,port='',user='',password='',input_map={},error_map={},session_pool_size=1,pool_timeout = 100):

        session = self._initiate_connection_manager(self.logger,session_type,ip,port,user,password,self.get_default_prompt())
        self.session = SessionHandler(session)
        return self.session

    def set_default_actions(self,default_actions_tuple):pass

    def initial_commands(self,actions):
        '''
        :param actions: [(action1,prompt),(action2,prompt)...] or (action,prompt)
        :return: None
        '''
        self._set_actions(actions)



    def _initiate_connection_manager(self,logger,session_type,ip,port,user,password,default_prompt,session_pool_size=1,pool_timeout=120):
        session = self._get_session(session_type,ip,port,user,password)
        CONNECTION_MAP=OrderedDict()
        CONNECTION_MAP[session_type] = session
        connection_manager = ConnectionManager.get_instance()
        connection_manager.logger = logger
        connection_manager.session_manager = SessionManager(logger=logger,connection_type=session_type,prompt=default_prompt,connection_map=CONNECTION_MAP)
        session = connection_manager.get_session_instance(connection_type=session_type, prompt=default_prompt)


        connection_manager.return_session_instance(session)

        return session

    def _get_session(self,session_type,ip,port,user,password):
        session_class = self._get_session_type(session_type)
        session = SessionCreator(session_class)
        session.proxy = SessionValidationProxy
        session.kwargs = {'host': ip,
                          'port': port}
        if (user != '' and password != ''):
            session.kwargs.update({'username': user,
                                   'password': password})
        return session


if __name__ == '__main__':
    default_mode = Command_mode('[>$#]/s*$', 'enter', 'exit')


    with cli.new_session(session_type=Cli.SSH,ip='192.168.28.150',user='root',password='Juniper', default_mode = default_mode) as default_session:
        default_session.run_command('show version',state.default)