#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 3:40 PM'

from ..util import run_command
from ..session import session_command


@session_command('ssh', 'list ssh hosts config')
def ssh_config(from_id, channel, args):
    return run_command('cat .ssh/config', channel)
