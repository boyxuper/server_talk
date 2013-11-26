#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'johnx'
__date__ = '11/18/13 1:20 PM'

import xmpp

from ..util import print_node, ensure_client, cached


class XMPPClient(object):
    client = None
    jid = None

    def __init__(self, jid, password, server=None):
        self.login(jid, password, server)

    def _build_client(self, jid, password, server):
        client = xmpp.Client(jid.getDomain(), debug=[])
        if client.connect(server) == '':
            raise Exception('Cannot connect to server.')
        if client.auth(jid.getNode(), password) is None:
            raise Exception('Authentication failed.')

        # self.client.RegisterHandler('message', self.message_callback)
        # self.client.RegisterHandler('presence', self.presence_callback)
        # self.client.RegisterHandler('iq', self.iqHandler)
        client.sendInitPresence()

        return client

    def login(self, jid, password, server):
        if not isinstance(jid, xmpp.JID):
            jid = xmpp.JID(jid)

        self.jid = jid
        self.client = self._build_client(jid, password, server)

    def message_callback(self, client, message):
        """ 默认消息回调(可通过继承自定义) """

    def iqHandler(self, client, message):
        """ 默认消息回调(可通过继承自定义) """
        print message

    def presence_callback(self, client, msg_node):
        """ 默认事件回调,包括下面几个(可通过继承自定义) """
        print_node(msg_node)
        type_ = msg_node.getType()
        who = msg_node.getFrom().getStripped()

        if type_ == 'subscribe':
            self.subscribe(who)
        elif type_ == 'unsubscribe':
            self.unsubscribe(who)
        elif type_ == 'subscribed':
            self.subscribed(who)
        elif type_ == 'unsubscribed':
            self.unsubscribed(who)
        elif type_ in ('available', None):
            self.available(msg_node)
        elif type_ == 'unavailable':
            self.unavailable(who)

    def subscribe(self, jid):
        """ 加好友 """
        self.client.send(xmpp.Presence(to=jid, typ='subscribed'))
        self.client.send(xmpp.Presence(to=jid, typ='subscribe'))

    def unsubscribe(self, jid):
        """ 取消好友 """
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribe'))
        self.client.send(xmpp.Presence(to=jid, typ='unsubscribed'))

    def subscribed(self, jid):
        """ 已加 """

    def unsubscribed(self, jid):
        """ 已退 """

    def available(self, message):
        """ 上线 """

    def unavailable(self, jid):
        """ 下线 """

    def send_text(self, jid, content):
        """ 发消息给某人"""
        message = xmpp.protocol.Message(jid, content, attrs={
            'type': 'chat'
        })
        self.client.send(message)

    def __getattr__(self, item):
        return getattr(self.client, item)

    ensure_client = cached(60)(ensure_client)

    def loop(self):
        while True:
            try:
                self.ensure_client()
                self.client.Process(1)
            except KeyboardInterrupt:   # Ctrl+C停止
                return
