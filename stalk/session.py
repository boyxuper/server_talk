#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 2:07 PM'

import os
import paramiko
import functools

from .util import CONFIG
from .head_quarters import command


def session_command(*args, **kwargs):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(from_id, args):
            try:
                session = SessionManager.get_session(from_id)
                return func(channel=session['channel'], from_id=from_id, args=args)
            except NoSessionAvailable:
                return 'No session available for <%s>.' % from_id
        return command(*args, **kwargs)(wrapper)
    return decorator


class NoSessionAvailable(Exception):
    pass


class SessionManager(object):
    _users = {}
    _config = CONFIG['server']

    @classmethod
    def _make_client(cls):
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        private_keyfile = os.path.expanduser(os.path.join(*cls._config['private_key'].split('/')))
        client.connect(cls._config['host'], username=cls._config['user'], key_filename=private_keyfile)
        return client

    @classmethod
    def init_user(cls, user):
        assert user not in cls._users

        user_info = cls._users[user] = {
            'client': cls._make_client(),
            'sessions': {},
            'active': None,
            'max_id': 1,
        }

        return user_info

    @classmethod
    def init_session(cls, user, switch=True):
        user_info = cls._users.get(user) or cls.init_user(user)

        channel = user_info['client'].invoke_shell()
        channel.settimeout(.1)

        sessions = cls._users[user]
        sessions['sessions'][sessions['max_id']] = {
            'id': sessions['max_id'],
            'channel': channel,
        }

        if switch:
            sessions['active'] = sessions['sessions'][sessions['max_id']]
        sessions['max_id'] += 1

        return sessions['active']

    @classmethod
    def get_session(cls, user):
        if user not in cls._users:
            raise NoSessionAvailable

        sessions = cls._users[user]
        if sessions['active'] is None:
            raise NoSessionAvailable

        return sessions['active']

    @classmethod
    def _get_sessions(cls, user):
        if user not in cls._users:
            raise NoSessionAvailable

        return cls._users[user]

    @classmethod
    def get_sessions(cls, user):
        return cls._get_sessions(user)['sessions']

    @classmethod
    def switch_session(cls, user, session_id):
        sessions = cls._get_sessions(user)

        try:
            session_id = int(session_id)
            sessions['active'] = sessions['sessions'][session_id]
        except (KeyError, ValueError):
            raise NoSessionAvailable

        return sessions['active']

