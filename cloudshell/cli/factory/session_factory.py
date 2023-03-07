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
        self,
        resource_config,
        logger,
        on_session_start=None,
        access_key=None,
        access_key_passphrase=None,
    ):
        """Initialize session instance.

        Encapsulate the logic of the session instance creation.
        :param resource_config:
        :param logging.Logger logger:
        :param on_session_start: function that will be called on session start
        :param access_key: access key for the resource
        :param access_key_passphrase: access key passphrase for the resource
        """
        raise NotImplementedError


class GenericSessionFactory(SessionFactory):
    def init_session(
        self,
        resource_config,
        logger,
        on_session_start=None,
        access_key=None,
        access_key_passphrase=None,
    ):
        return self.session_class(
            **self._session_kwargs(
                resource_config,
                logger,
                on_session_start,
                access_key,
                access_key_passphrase,
            )
        )

    @property
    def SESSION_TYPE(self):
        return self.session_class.SESSION_TYPE

    def _session_kwargs(
        self,
        resource_config,
        logger,
        on_session_start,
        access_key,
        access_key_passphrase,
    ):
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "on_session_start": on_session_start,
        }


class CloudInfoAccessKeySessionFactory(GenericSessionFactory):
    def _session_kwargs(
        self,
        resource_config,
        logger,
        on_session_start,
        access_key,
        access_key_passphrase,
    ):
        return {
            "host": resource_config.address,
            "username": resource_config.user,
            "password": resource_config.password,
            "port": resource_config.cli_tcp_port,
            "pkey": access_key,
            "pkey_passphrase": access_key_passphrase,
            "on_session_start": on_session_start,
        }
