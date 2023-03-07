#!/usr/bin/python
# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractmethod

ABC = ABCMeta("ABC", (object,), {"__slots__": ()})


class SessionFactory(ABC):
    """Session factory.

    Help to initialize session for specified session class.
    """

    def __init__(self, session_class):
        """:param session_class: Session class."""
        self.session_class = session_class

    @abstractmethod
    def init_session(
        self, resource_config, logger, reservation_context=None, on_session_start=None
    ):
        """Initialize session instance.

        Encapsulate the logic of the session instance creation.
        :param resource_config:
        :param logging.Logger logger:
        :param ReservationContextDetails reservation_context:  # todo remove context
        """
        raise NotImplementedError


class GenericSessionFactory(SessionFactory):
    def init_session(
        self, resource_config, logger, reservation_context=None, on_session_start=None
    ):
        return self.session_class(
            **self._session_kwargs(
                resource_config, logger, reservation_context, on_session_start
            )
        )

    @property
    def SESSION_TYPE(self):
        return self.session_class.SESSION_TYPE

    def _on_session_start(self, session, logger):
        """Perform some default commands when session just opened.

        Like 'no logging console'
        """
        pass

    def _session_kwargs(
        self, resource_config, logger, reservation_context=None, on_session_start=None
    ):
        on_session_start = on_session_start or self._on_session_start
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "on_session_start": on_session_start,
        }


class CloudInfoAccessKeySessionFactory(GenericSessionFactory):
    def _session_kwargs(
        self, resource_config, logger, reservation_context=None, on_session_start=None
    ):
        on_session_start = on_session_start or self._on_session_start
        access_key = getattr(reservation_context, "cloud_info_access_key", "")
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "pkey": access_key,
            "on_session_start": on_session_start,
        }
