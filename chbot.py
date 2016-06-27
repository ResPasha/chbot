#!/usr/bin/env python
import traceback

from db_helper import DBHelper
from controls import *
from models import User
from bot import Bot
import config
import strings


class CHBot:
    def __init__(self):
        self.db = DBHelper()
        self.bot = Bot()
        self.controls = {}
        self.bot.message_loop(
            {
                'chat': self.handle,
                'callback_query': self.on_callback
            }
        )

    def on_callback(self, callback_query):
        data = callback_query['data']
        control_name = data.split('#')[0]
        control = self.controls[control_name]
        control.process(callback_query)
        return

    def handle_master_reply(self, msg):
        assert 'text' in msg, 'master_reply first fuckup: no text'
        text = msg['text']
        # commands
        assert 'reply_to_message' in msg, 'master_reply second fuckup: no replied'
        replied = msg['reply_to_message']
        if 'forward_from' in replied:
            self.feedback_reply(msg)
            return True

    def handle_text(self, msg):
        text = msg['text']

        # Master commands
        if text == strings.cmd_start:
            # TODO: check for existence
            m = Menu('main', {
                'Intro': 'Hello there!',
                'Help': 'Little help',
                'Info': 'Source code, author and contact info'
            })
            self.controls[m.name] = m
            m.send(msg['from']['id'])
            return
        if text == strings.cmd_users:
            # TODO: check for existence
            p = Pager('u', self.db.get(self.db.usr, User))
            p.title = strings.msg_users
            self.controls[p.name] = p
            p.send(msg['from']['id'])
            return
        elif text.startswith(strings.cmd_user):
            # TODO: check for existence
            user_id = int(text.split('r')[1])
            h = History('h', user_id)  # FIXME
            self.controls[h.name] = h
            return

        # replied
        if 'reply_to_message' in msg:
            if self.handle_master_reply(msg):
                return

        # Else
        self.bot.sendMessage(config.master, strings.errmsg_unknown_cmd,
                             reply_to_message_id=msg['message_id'])
        self.handle_feedback(msg)

    def handle_feedback(self, msg):
        sender = User(**msg['from'])
        self.db.sync(self.db.usr, sender)
        if 'text' in msg:
            if msg['text'] == strings.cmd_start:
                self.bot.sendMessage(sender.id, strings.msg_start)
        if 'forward_from' in msg:
            pass  # TODO: add userblock
        self.bot.forwardMessage(config.master, sender.id, msg['message_id'])

    def handle(self, msg):
        sender = User(**msg['from'])
        try:
            if str(sender.id) != config.master:  # or sender.type = master?
                self.handle_feedback(msg)
                return
            if 'text' in msg:
                self.handle_text(msg)
                return
        except Exception as e:
            traceback.print_exc()
            text = strings.errmsg_err + '\n'
            text += str(type(e)) + '\n'
            text += str(e)
            if str(sender.id) == config.master:
                error = msg
            else:
                error = self.bot.forwardMessage(config.master, sender.id, msg['message_id'])
            self.bot.sendMessage(config.master, text, reply_to_message_id=error['message_id'])

    def feedback_reply(self, msg):
        assert 'reply_to_message' in msg, 'feedback_reply first fuckup: no replied'
        assert 'text' in msg, 'feedback_reply second fuckup: no text'
        # TODO should be any type, not text only
        recipient = User(**msg['reply_to_message']['forward_from'])
        text = msg['text']
        self.bot.sendMessage(recipient.id, text)
        self.bot.sendMessage(config.master, strings.msg_reply_sent,
                             reply_to_message_id=msg['message_id'])
