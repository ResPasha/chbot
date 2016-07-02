#!/usr/bin/env python
# import traceback

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

    def on_callback(self, _callback_query):
        callback_query = CallbackQuery(**_callback_query)
        data = callback_query.data
        control_name = data.split('#')[0]
        control = self.controls.get(control_name)
        if control:
            self.process_control(control, callback_query)
        else:
            self.process_control(control_name, callback_query)

    def process_control(self, control, callback_query=None, cmd_from_id=None):
        assert callback_query or cmd_from_id
        if isinstance(control, Control):
            control.process(callback_query)
        else:
            control_name = control
            control = None
            if control_name == 'mmain':
                control = Menu('main', [
                    ('Intro', 'Hello there!'),
                    ('Help', 'Little help'),
                    ('Info', 'Source code, author and contact info')
                ])
            elif control_name == 'pu':
                control = Pager('u', self.db.usr.get_all())
                control.title = strings.msg_users
            elif control_name.startswith('user'):
                pass  # TODO: show user info
            else:
                raise ValueError('No control constructor with such name')
            self.controls[control_name] = control
            if callback_query:
                control.process(callback_query)
            else:
                control.send(cmd_from_id)

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
        text = msg.text

        # Master commands
        if text == strings.cmd_start:
            self.process_control('mmain', cmd_from_id=msg.from_.id)
        elif text == strings.cmd_users:
            self.process_control('pu', cmd_from_id=msg.from_.id)
        elif text.startswith(strings.cmd_user):
            self.process_control(text[1:], cmd_from_id=msg.from_.id)

        # replied
        if 'reply_to_message' in msg:
            if self.handle_master_reply(msg):
                return

        # Else
        self.bot.sendMessage(config.master, strings.errmsg_unknown_cmd,
                             reply_to_message_id=msg.message_id)
        self.handle_feedback(msg)

    def handle_feedback(self, msg):
        sender = msg.from_
        if msg.text:
            if msg.text == strings.cmd_start:
                self.bot.sendMessage(sender.id, strings.msg_start)
        if msg.forward_from:
            pass  # TODO: add userblock
        self.bot.forwardMessage(config.master, sender.id, msg.message_id)

    def handle(self, _msg):
        msg = Message(**_msg)
        sender = self.db.usr.get_by_id(msg.from_.id)
        sender.update(msg.from_)
        try:
            if str(sender.id) != config.master:  # or sender.type = master?
                self.handle_feedback(msg)
                return
            if msg.text:
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
                error_msg = self.bot.forwardMessage(config.master, sender.id, msg.message_id)
                error = Message(**error_msg)
            self.bot.sendMessage(config.master, text, reply_to_message_id=error.message_id)
        self.db.usr.update(sender)

    def feedback_reply(self, msg):
        assert 'reply_to_message' in msg, 'feedback_reply first fuckup: no replied'
        assert 'text' in msg, 'feedback_reply second fuckup: no text'
        # TODO should be any type, not text only
        recipient = User(**msg['reply_to_message']['forward_from'])
        text = msg['text']
        self.bot.sendMessage(recipient.id, text)
        self.bot.sendMessage(config.master, strings.msg_reply_sent,
                             reply_to_message_id=msg['message_id'])
