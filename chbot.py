#!/usr/bin/env python
import traceback

from telepot.namedtuple import CallbackQuery, Message

from db_helper import DBHelper
from bot import Bot
import mycontrol
import model
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
        control = self.get_control(control_name, callback_query.from_)
        control.process(callback_query)

    def get_control(self, control_name, invoker):
        if str(invoker.id) != config.master and \
                        control_name not in ['start', 'error']:
            return self.get_control(strings.cmd_error, invoker)
        control = self.controls.get(control_name)
        if not control:
            if control_name == strings.cmd_start:
                control = mycontrol.StartMenu()
            elif control_name == strings.cmd_users:
                control = mycontrol.UserListControl()
            elif control_name.startswith(strings.cmd_user):
                control = mycontrol.UserControl(control_name.split('r')[1])
            else:
                control = self.get_control(strings.cmd_error, invoker)
            self.controls[control_name] = control
        return control

    def handle(self, _msg):
        msg = Message(**_msg)  # TODO: create own message object
        # TODO: log msg in db
        user = self.db.usr.get_by_id(msg.from_.id)
        if not user:
            user = model.User(id=msg.from_id, first_name=msg.from_.first_name)
        user.update(msg.from_)
        try:
            if msg.text and msg.text.startswith('/'):
                control = self.get_control(msg.text[1:], user)
                control.send(user.id)
            elif msg.reply_to_message and str(user.id) == config.master:
                self.resend(msg)
                pass  # TODO: log
            elif str(user.id) != config.master:
                if msg.forward_from:
                    control = self.get_control(strings.cmd_user + str(user.id),
                                               self.db.usr.get_by_id(config.master))
                    control.send(config.master)
                self.bot.forwardMessage(config.master, user.id, msg.message_id)
                pass  # TODO: log
            else:
                self.bot.sendMessage(user.id, strings.errmsg_unknown_cmd,
                                     reply_to_message_id=msg.message_id)
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
        assert msg.text  # TODO should be any type, bot text only
        replied = msg.reply_to_message
        if replied.forward_from:
            recipient_id = replied.forward_from.id
        else:
            recipient_id = replied.text.split('\n')[0].split('r')[1]
        text = msg.text
        self.bot.sendMessage(recipient_id, text)
        self.bot.sendMessage(config.master, strings.msg_reply_sent,
                             reply_to_message_id=msg.message_id)
