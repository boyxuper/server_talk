#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 4:19 PM'


from ..head_quarters import command, InvalidCommandSyntax
from ..session import SessionManager, session_command
from ..util import run_command, print_channel


@command('init', 'init a new session')
def init_session(from_id, args):
    session = SessionManager.init_session(from_id)
    return run_command(None, session['channel'])


@command('sw', 'switch session')
def init_session(from_id, args):
    """switch activated session,
    use %cl.sl for session list.

    syntax:
        %cl.sw <session_id>
    """
    if not args.isdigit():
        raise InvalidCommandSyntax

    session = SessionManager.switch_session(from_id, session_id=args)
    return run_command('\n', session['channel'])


@session_command('sl', 'list sessions')
def list_sessions(from_id, channel, args):
    sessions = SessionManager.get_sessions(from_id)
    active_id = SessionManager.get_session(from_id)['id']
    return '\r\n'.join(
        '[%s] -> %s%s' % (
            s['id'], '[*active]' * (s['id'] == active_id), print_channel(s['channel'])
        ) for s in sessions.values())
