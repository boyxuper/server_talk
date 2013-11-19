#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 3:13 PM'

from ..head_quarters import command, HeadQuarters, InvalidCommandSyntax


@command('', 'help')
def help_menu(from_id, args):
    commands = sorted(HeadQuarters.list_commands(), key=lambda cmd: cmd['priority'])
    return '\r\n'.join(HeadQuarters.describe_command(cmd, short=True) for cmd in commands if cmd['name'])


@command('?', 'help')
def help_menu(from_id, args):
    args = args.strip()
    if ' ' in args:
        raise InvalidCommandSyntax

    command = HeadQuarters.get_command(args)
    return HeadQuarters.describe_command(command)

