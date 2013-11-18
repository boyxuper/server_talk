#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 3:13 PM'

from ..head_quarters import command, HeadQuarters


@command('', 'help')
def help_menu(from_id, args):
    commands = sorted(HeadQuarters._registry.values(), key=lambda cmd: cmd['priority'])
    return '\r\n'.join('?%(cmd)s -> %(summary)s' % command for command in commands if command['cmd'])

