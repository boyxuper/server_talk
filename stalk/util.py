#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 1:12 PM'

import os
import re
import yaml
import socket


CONFIG = {}
ROOT_PATH = os.path.join(os.path.dirname(__file__), '..')


def make_path(*args):
    return os.path.join(ROOT_PATH, *args)


def dump_dict(d, keys):
    return {key: d[key] for key in keys if key in d}


def print_node(node, indent=1):
    print node
    # pprint(dump_dict(node.__dict__, ['name', 'props', 'attrs']), indent=indent)
    # map(partial(print_node, indent=indent + 2), node.kids or [])


def _read_config():
    global CONFIG
    CONFIG = yaml.load(open(make_path('config.yaml'), 'rb').read())

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


def describe_channel(channel):
    def _describe(channel):
        result = ''
        if channel.closed:
            result += 'closed'
        elif channel.active:
            result += 'open'
            if channel.eof_received:
                result += ' <EOF received>'
            if channel.eof_sent:
                result += ' <EOF sent>'
            # if len(channel.in_buffer) > 0:
            #     result += ' in-buffer=%d' % (len(channel.in_buffer),)
        return result
    return '[%s -> %s]' % (_describe(channel), describe_transport(channel.transport))


def describe_transport(transport):
    if not transport.active:
        return 'inactivated'
    elif transport.is_authenticated():
        return 'authenticated'
    else:
        return 'awaiting authentication'


command_lead = CONFIG['command_lead']


def render_command_lead(template, arg=None):
    template = template % arg if arg else template
    return template.replace('%cl.', command_lead)


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
