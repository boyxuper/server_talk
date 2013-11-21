#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 1:11 PM'


from stalk.session import SessionManager
from stalk.util import make_client, run_command, CONFIG
from stalk.head_quarters import HeadQuarters, CommandNotImplemented

admin_email = CONFIG['admin_email']
command_lead = CONFIG['command_lead']


def process_message(_, message_node):
    from_id = message_node.getFrom().getStripped()
    content = message_node.getBody()

    if not content:
        return

    print '%s: %s' % (from_id, content)
    if from_id == admin_email:
        if content.startswith(command_lead):
            try:
                client.send_text(from_id, HeadQuarters.handle(from_id, content))
            except CommandNotImplemented as err:
                client.send_text(from_id, 'command not found: %s%s.' % (command_lead, err.name))
        else:
            admin_channel = SessionManager.get_session(from_id)['channel']
            client.send_text(from_id, run_command(content, admin_channel))

if __name__ == '__main__':
    HeadQuarters.load_all_commands()

    client = make_client()
    client.RegisterHandler('message', process_message)
    client.loop()
