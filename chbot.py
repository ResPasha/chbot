#!/usr/bin/env python
import telepot
import requests
from time import sleep

import hires_finder
from db_helper import DBHelper
import config
import strings

class CHBot:
    def __init__(self):
        self.bot = None
        self.bot = telepot.Bot(config.TOKEN)
        self.bot.notifyOnMessage({'normal': self.on_normal_message})

        self.last_image = None
        self.running = False

        self.db_helper = DBHelper()

    def run(self):
        self.running = True
        self.bot.sendMessage(config.master, strings.started)
        while self.running:
            sleep(10)
        self.bot.sendMessage(config.master, strings.stopped)

    def try_publish(self, image):
        caption = self.db_helper.get_caption(image)
        reply_markup = {'keyboard': [
            [strings.publish_cmd, strings.publish_nsfw_cmd],
            [strings.edit_c_cmd, strings.add_tag_cmd, strings.cancel_publish_cmd]
        ], 'resize_keyboard': True}
        self.last_image = image
        self.bot.sendMessage(config.master, caption, reply_markup=reply_markup)

    def handle_photo(self, msg):
        self.bot.sendChatAction(config.master, 'upload_photo')
        file_id = msg['photo'][-1]['file_id']
        file_path = self.bot.getFile(file_id)['file_path']
        file_link = 'https://api.telegram.org/file/bot' + config.TOKEN + '/' + file_path
        file = requests.get(file_link).content
        image = hires_finder.get_hires(file)
        image.file_id = file_id
        self.db_helper.add(image)
        self.try_publish(image)
        
    def handle_master_reply(self, msg):
        assert 'text' in msg, 'master_reply first fuckup: no text'
        text = msg['text']
        assert 'reply_to_message' in msg, 'master_reply second fuckup: no replied'
        replied = msg['reply_to_message']
        if 'forward_from' in replied:
            self.feedback_reply(msg)
            return True
        assert 'text' in replied, 'master_reply third fuckup: replied is not text'
        replied_text = replied['text']
        if replied_text == strings.cr_tag_editing:
            if text == strings.cancel_cmd:
                self.bot.sendMessage(config.master, strings.cancel_confirm)
                return True
            if text == strings.empty_cmd:
                text = ''
            self.db_helper.add_cr_rule(text, self.last_image.copyright_tag)
            self.try_publish(self.last_image)
            return True
        if replied_text == strings.extra_tag_editing:
            if text == strings.empty_cmd:
                self.last_image.extra_tags = []
                self.db_helper.update(self.last_image)
                self.try_publish(self.last_image)
                return True
            if text == strings.cancel_cmd:
                self.bot.sendMessage(config.master, strings.cancel_confirm)
                return True
            self.last_image.extra_tags.append(text)
            self.db_helper.update(self.last_image)
            self.try_publish(self.last_image)
            return True
        hires_link = replied_text.split('\n', 1)[0]
        image = self.db_helper.find_by_link(hires_link)
        if not image:
            self.bot.sendMessage(config.master, strings.db_err,
                                 reply_to_message_id=replied['message_id'])
            return True
        if text == strings.publish_cmd:
            photo = image.file_id
            self.bot.sendPhoto(config.channel,
                               photo=photo,
                               caption=self.db_helper.get_caption(image))
            self.db_helper.delete(image)
            # TODO db_helper.add_published(image)
            self.bot.sendMessage(config.master, strings.publish_confirm,
                                 reply_markup={'hide_keyboard': True})
            return True
        if text == strings.publish_nsfw_cmd:
            photo = image.file_id
            self.bot.sendPhoto(config.nsfw_channel,
                               photo=photo,
                               caption=self.db_helper.get_nsfw_caption(image))
            self.db_helper.delete(image)
            # TODO db_helper.add_nsfw(image)
            self.bot.sendMessage(config.master, strings.publish_nsfw_confirm,
                                 reply_markup={'hide_keyboard': True})
            return True
        if text == strings.cancel_publish_cmd:
            self.db_helper.delete(image)
            self.bot.sendMessage(config.master, strings.cancel_publish_confirm,
                                 reply_markup={'hide_keyboard': True})
            return True
        if text == strings.edit_c_cmd:
            self.last_image = image
            self.bot.sendMessage(config.master, strings.cr_tag_editing,
                                 reply_markup={'force_reply': True})
            return True
        if text == strings.add_tag_cmd:
            self.last_image = image
            self.bot.sendMessage(config.master, strings.extra_tag_editing,
                                 reply_markup={'force_reply': True})
            return True
        return False

    def handle_text(self, msg):
        text = msg['text']

        # Master commands
        if text == strings.term_cmd:
            self.running = False
            return
        # TODO implement the following Master commands
        if text == strings.help_cmd: return
        if text == strings.not_posted_list_cmd: return
        if text == strings.users_cmd: return

        # replied
        if 'reply_to_message' in msg:
            if self.handle_master_reply(msg):
                return

        # Else
        self.bot.sendMessage(config.master, strings.unkn_cmd_err,
                             reply_to_message_id=msg['message_id'])
        self.handle_feedback(msg)

    def handle_feedback(self, msg):
        sender = msg['from']
        # TODO add user to db
        if 'text' in msg:
            if msg['text'] == '/start':
                self.bot.sendMessage(sender['id'], strings.welcoming)
            if msg['text'] == '/ping':
                self.bot.sendMessage(sender['id'], strings.ping_thankie)
        if 'photo' in msg:
            self.bot.sendMessage(sender['id'],
                                 strings.suggestion_thankie,
                                 reply_to_message_id=msg['message_id'])
            self.handle_photo(msg)
        if 'sticker' in msg:
            self.bot.sendMessage(sender['id'],
                                 strings.suggestion_thankie,
                                 reply_to_message_id=msg['message_id'])
        self.bot.forwardMessage(config.master, sender['id'], msg['message_id'])

    def handle_sticker(self, msg):
        pass  # TODO publish on anime_stickers

    def on_normal_message(self, msg):
        sender = msg['from']
        try:
            if str(sender['id']) != config.master:
                self.handle_feedback(msg)
                return
            if 'photo' in msg:
                self.handle_photo(msg)
                return
            if 'text' in msg:
                self.handle_text(msg)
                return
            if 'sticker' in msg:
                self.handle_sticker(msg)
                return
        except Exception as e:
            text = strings.other_err + '\n'
            text += str(type(e)) + '\n'
            text += str(e)
            if str(sender['id']) == config.master:
                error = msg
            else:
                error = self.bot.forwardMessage(config.master, sender['id'], msg['message_id'])
            self.bot.sendMessage(config.master, text, reply_to_message_id=error['message_id'])

    def feedback_reply(self, msg):
        assert 'reply_to_message' in msg, 'feedback_reply first fuckup: no replied'
        assert 'text' in msg, 'feedback_reply second fuckup: no text'
        # TODO should be any type, not text only
        recipient = msg['reply_to_message']['forward_from']
        text = msg['text'] + strings.maid_footer
        self.bot.sendMessage(recipient['id'], text)
        self.bot.sendMessage(config.master, 'Sent, Master!',
                             reply_to_message_id=msg['message_id'])

bot = CHBot()
bot.run()
