from cloudshell.cli.service.cli_exception import CliException
from cloudshell.cli.service.session_manager import SessionManager


class SessionManagerException(CliException):
    pass


class SessionManagerImpl(SessionManager):
    def __init__(self):
        self._existing_sessions = []

    def new_session(self, new_sessions, prompt, logger):
        """Create new session.

        :param new_sessions
        :type new_sessions: list
        :param prompt:
        :param logger:
        :return:
        """
        if not isinstance(new_sessions, list):
            new_sessions = [new_sessions]

        for session in new_sessions:
            try:
                session.connect(prompt, logger)
                logger.debug("Created new {} session".format(session.session_type))
                self._existing_sessions.append(session)
                return session
            except Exception as e:
                logger.debug(e)
        raise SessionManagerException(
            self.__class__.__name__,
            "Failed to create new session for type {}, see logs for details".format(
                ", ".join([session.session_type for session in new_sessions])
            ),
        )

    def existing_sessions_count(self):
        """Count of existing sessions.

        :rtype: int
        """
        return len(self._existing_sessions)

    def remove_session(self, session, logger):
        """Remove session.

        :param session:
        :param logger:
        """
        if session in self._existing_sessions:
            self._existing_sessions.remove(session)
            logger.debug("{} session was removed".format(session.session_type))

    def is_compatible(self, session, new_sessions, logger):
        """Compare session with new session parameters.

        :type session: Session
        """
        if not isinstance(new_sessions, list):
            new_sessions = [new_sessions]

        if session in self._existing_sessions:
            compatible = False
            for new_session in new_sessions:
                if new_session == session:
                    compatible = True
                    break
            return compatible
        else:
            raise SessionManagerException(self.__class__.__name__, "Unknown session")
