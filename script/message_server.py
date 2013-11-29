#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/21/13 4:51 PM'


import threading
from bottle import get, post, run, request, debug

from stalk.util import make_client, CONFIG


config = CONFIG['message_server']


def process_message(_, message_node):
    from_id = message_node.getFrom().getStripped()
    content = message_node.getBody()

    if not content:
        return

    if content == 'hi':
        client.send_text(from_id, 'hi: %s' % from_id)


@get('/send_alert')
def send_alert_page():
    return """
    <html><body>
    <form method="post">
    <input name="message" />
    <br />
    <input type="submit">
    </form>
    </body></html>
    """


@post('/send_alert')
def send_alert():
    for target in config['recipients']:
        client.send_text(target, request.POST['message'])

    return 'success'

if __name__ == '__main__':
    client = make_client()
    client.RegisterHandler('message', process_message)
    debug(config['debug'])
    threading.Thread(target=client.loop).start()
    run(host=config['bind'], port=config['port'])

