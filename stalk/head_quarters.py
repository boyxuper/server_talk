#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 3:06 PM'

import os

from .util import render_command_lead, strip_doc_string, make_path, command_lead


def command(name, summary, priority=None):
    def decorator(func):
        HeadQuarters.register(
            name, summary, func, strip_doc_string(func.__doc__), priority
        )
        return func
    return decorator


class CommandNotImplemented(Exception):
    def __init__(self, name, *args, **kwargs):
        super(CommandNotImplemented, self).__init__(*args, **kwargs)
        self.name = name


class InvalidCommandSyntax(Exception):
    pass


class HeadQuarters(object):
    _registry = {}

    @classmethod
    def register(cls, name, summary, handler, description=None, priority=None):
        cls._registry[name] = {
            'name': name,
            'summary': summary,
            'description': description,
            'handler': handler,
            'priority': priority,
        }

    @classmethod
    def handle(cls, from_id, cmd):
        assert cmd.startswith(command_lead)
        if ' ' in cmd:
            name, args = cmd[len(command_lead):].split(' ', 1)
        else:
            name, args = cmd[len(command_lead):], ''

        command = cls.get_command(name)

        try:
            return command['handler'](from_id, args)
        except InvalidCommandSyntax:
            return 'Invalid Syntax: "%s"\r\n%s' % (
                cmd, cls.describe_command(command)
            )

    @classmethod
    def get_command(cls, name):
        command = cls._registry.get(name)
        if command is None:
            raise CommandNotImplemented(name)

        return command

    @classmethod
    def list_commands(cls):
        return HeadQuarters._registry.values()

    @staticmethod
    def describe_command(command, short=False):
        short = short or not command['description']

        template = \
            '%cl.%(name)s -> %(summary)s' if short else \
            '%cl.%(name)s -> %(summary)s\r\n\r\n%(description)s'

        return render_command_lead(template, command)

    @classmethod
    def load_all_commands(cls):
        root_path = make_path('stalk', 'command')
        cmd_file = lambda name: \
            name.endswith('.py') \
            and not name.startswith('__') \
            and os.path.isfile(os.path.join(root_path, name))

        for mod in filter(cmd_file, os.listdir(root_path)):
            __import__('stalk.command.' + mod[:-3])
