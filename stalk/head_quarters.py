#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 3:06 PM'

import os


def command(cmd, summary, priority=None):
    def decorator(func):
        HeadQuarters.registry(cmd, summary, func, priority)
        return func

    return decorator


class CommandNotImplemented(Exception):
    pass


class InvalidCommandSyntax(Exception):
    pass


class HeadQuarters(object):
    _registry = {}

    @classmethod
    def registry(cls, cmd, summary, handler, priority=None):
        cls._registry[cmd] = {
            'cmd': cmd,
            'summary': summary,
            'handler': handler,
            'priority': priority,
        }

    @classmethod
    def handle(cls, from_id, cmd):
        assert cmd[0] == '?'
        if ' ' in cmd:
            cmd, args = cmd[1:].split(' ', 1)
        else:
            cmd, args = cmd[1:], ''

        command = cls._registry.get(cmd)
        if command is None:
            raise CommandNotImplemented

        try:
            return command['handler'](from_id, args)
        except InvalidCommandSyntax:
            return 'invalid syntax: %(cmd)s -> %(summary)s' % command

    @classmethod
    def load_all_commands(cls):
        root_path = os.path.join(os.path.dirname(__file__), 'command')
        cmd_file = lambda name: \
            name.endswith('.py') \
            and not name.startswith('__') \
            and os.path.isfile(os.path.join(root_path, name))

        for mod in filter(cmd_file, os.listdir(root_path)):
            __import__('stalk.command.' + mod[:-3])
