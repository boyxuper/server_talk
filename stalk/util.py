#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 1:12 PM'

import yaml
from pprint import pprint
from functools import partial
import re
import socket


CONFIG = {}


def dump_dict(d, keys):
    return {key: d[key] for key in keys if key in d}


def print_node(node, indent=1):
    print node
    # pprint(dump_dict(node.__dict__, ['name', 'props', 'attrs']), indent=indent)
    # map(partial(print_node, indent=indent + 2), node.kids or [])


def _read_config():
    global CONFIG
    CONFIG = yaml.load(open('../config.yaml').read())

_read_config()


def make_client():
    JABBER = CONFIG['jabber']
    from .client import JabberClient
    client = JabberClient(JABBER['id'], JABBER['passwd'], JABBER['server'])
    return client


ansi_escape = re.compile(r'\x1b[^m]*m')
ansi_escape2 = re.compile(r'\x1b\[[HJ]')


def escape_cleanup(text):
    """@see http://ascii-table.com/ansi-escape-sequences-vt-100.php"""
    return ansi_escape2.sub('', ansi_escape.sub('', text))


def read_until_prompt(channel):
    while not channel.closed:
        try:
            result = escape_cleanup(channel.recv(99999))
            yield result
            if not channel.recv_ready():
                if result.endswith(']$ ') or result.endswith(']# '):
                    return
        except socket.timeout:
            continue


def run_command(command, channel, wait_prompt=True):
    if command is not None:
        channel.send(command + '\n')
    else:
        command = ''

    result = ''.join(read_until_prompt(channel))
    if result.startswith(command + '\r\n'):
        result = result[len(command) + 2:]

    return result.strip()


def print_channel(channel):
    old = repr(channel)[18:-2].split(' ', 1)[1]
    return '<%s>' % old.replace('-> <paramiko.Transport at ', '')


command_lead = CONFIG['command_lead']


def render_command_lead(template, arg=None):
    template = template.replace('%cl.', command_lead)
    return template % arg if arg else template


space_lead_re = re.compile(r'^(\s+)')


def strip_doc_string(text, sep='\n'):
    if not text:
        return text

    lines = text.splitlines()
    for line in lines:
        match = space_lead_re.match(line)
        if match:
            leading_space = match.group()
            break
    else:
        return text

    remove_lead = lambda s: s[len(leading_space):] if s.startswith(leading_space) else s
    return sep.join(remove_lead(line) for line in lines)
