#!/usr/bin/env python
# import traceback

from db_helper import DBHelper
from control import *
from model import User
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
        control = self.get_control(control_name)
        control.process(callback_query)

    def get_control(self, control_name):
        control = self.controls.get(control_name)
        if not control:
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
                control = UserInfoControl(control_name.split('r')[1])
            else:
                raise ValueError('No control constructor with such name')
            self.controls[control_name] = control
        return control

    def handle(self, _msg):
        msg = Message(**_msg)  # TODO: create own message object
        # TODO: log msg in db
        user = self.db.usr.get_by_id(msg.from_.id)
        if not user:
            user = User(**msg.from_)
        user.update(msg.from_)
        try:
            if msg.text:
                control = self.get_control(msg.text[1:])
                control.send(user.id)
            elif msg.reply_to_message:  # TODO: check user.type
                self.resend(msg)
                pass  # TODO: log
            else:  # TODO: check user.
                if msg.forward_from:
                    control = self.get_control('user' + str(user.id))
                    control.send(config.master)
                self.bot.forwardMessage(config.master, user.id, msg.message_id)
                pass  # TODO: log
        except Exception as e:
            traceback.print_exc()
            text = strings.errmsg_err + '\n'
            text += str(type(e)) + '\n'
            text += str(e)
            if str(user.id) == config.master:
                error = msg
            else:
                error_msg = self.bot.forwardMessage(config.master, user.id, msg.message_id)
                error = Message(**error_msg)
            self.bot.sendMessage(config.master, text, reply_to_message_id=error.message_id)
        self.db.usr.update(user)

    def resend(self, msg):
        pass  # TODO: implement
