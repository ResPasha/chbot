from collections import namedtuple

from telepot.namedtuple import *
from telepot.exception import TelegramError
from bot import Bot
import strings

ProcessResult = namedtuple('ProcessResult',
                           [
                               'answer_text',
                               'show_alert',
                               'to_update'
                           ])
UPDATE_TEXT = 0
UPDATE_CAPTION = 1
UPDATE_REPLY_MARKUP = 2


class Control:
    def __init__(self, type, name):
        self.bot = Bot(None)
        self.type = type
        self.name = self.type + name

    def process(self, _query):
        query = CallbackQuery(**_query)
        assert query.data.startswith(self.name)
        user = query.from_
        if query.message:
            msg_identifier = (str(user.id), str(query.message.message_id))
        else:
            msg_identifier = str(query.inline_message_id)
        data = query.data.split('#')[1]

        answer_text, show_alert = None, None
        try:
            result = self._process(data)
            assert isinstance(result, ProcessResult)
            answer_text, show_alert, to_update = result
            if to_update == UPDATE_TEXT:
                self.bot.editMessageText(
                    msg_identifier,
                    self._get_text(data),
                    reply_markup=self.get_inline_kb(data)
                )
            elif to_update == UPDATE_CAPTION:
                self.bot.editMessageCaption(
                    msg_identifier,
                    self._get_caption(data),
                    reply_markup=self.get_inline_kb(data)
                )
            elif to_update == UPDATE_REPLY_MARKUP:
                self.bot.editMessageReplyMarkup(
                    msg_identifier,
                    reply_markup=self.get_inline_kb(data)
                )
        except TelegramError:
            pass
        except Exception:
            answer_text = "An error occured"
            show_alert = True

        if answer_text:
            self.bot.answerCallbackQuery(query.id, answer_text, show_alert)

    def send(self, user_id):
        self.bot.sendMessage(
            user_id,
            self._get_text(),
            reply_markup=self.get_inline_kb()
        )

    def get_inline_kb(self, *args):
        kb = self._get_inline_kb(*args)
        if kb:
            for row in kb:
                for button in row:
                    button.callback_data = self.name + '#' + button.callback_data
            return InlineKeyboardMarkup(inline_keyboard=kb)
        return None

    def _get_inline_kb(self, *args):
        raise NotImplementedError

    def _process(self, data):
        raise NotImplementedError

    def _get_text(self, *args):
        raise NotImplementedError

    def _get_caption(self, *args):
        raise NotImplementedError


class Pager(Control):
    def __init__(self, name, list):
        super().__init__("p", name)
        self.list = list
        self.items_per_page = 3
        self.title = ""
        self.default_page_no = 1

    def _get_text(self, data=None):
        page_no = int(data) if data else self.default_page_no
        text = self.title + '\n'
        left = (page_no - 1) * self.items_per_page
        right = left + self.items_per_page
        for item in self.list[left:right]:
            text += str(item) + '\n'
        return text

    def _get_inline_kb(self, data=None):
        page_no = int(data) if data else self.default_page_no
        button_row = []
        if len(self.list) < self.items_per_page:
            max_page_no = 1
        else:
            max_page_no = len(self.list) // self.items_per_page
        left = page_no - 2 if page_no > 2 else 1
        right = left + 5 if left + 5 <= max_page_no else max_page_no
        if left == right == 1:
            return None
        for i in range(left, right):
            if i == page_no:
                text = '*' + str(i) + '*'
            else:
                text = '.' + str(i) + '.'
            query = page_no
            button_row.append(InlineKeyboardButton(text=text, callback_data=str(i)))
        return [button_row]

    def _process(self, data):
        if data:
            return ProcessResult(strings.ca_done, False, UPDATE_TEXT)


class History(Pager):
    def __init__(self, user_id):
        self.user = db.get_user(user_id)
        super().__init__("u" + str(user_id), self.user.get_log())
        self.items_per_page = 5
        self.title = str(self.user)
        self.notification = self.user.notify

    def _get_inline_kb(self, data=None):
        kb = []
        kb.append(InlineKeyboardButton(text=strings.cb_block, callback_data='b'))
        kb.append(InlineKeyboardButton(text=strings.cb_notify, callback_data='n'))
        pages = super().get_inline_kb(data)
        pages.extend(kb)
        return pages

    def _process(self, data):
        if data == 'b':
            db_block_user
        elif data == 'n':
            db_toggle_notifications
            self.title = str(db_user)
            if notify:
                return ProcessResult(strings.ca_notify_on, False, UPDATE_TEXT)
            else:
                return ProcessResult(strings.ca_notify_off, False, UPDATE_TEXT)
        else:
            return super()._process(data)

class Counter(Control):
    def __init__(self):
        super().__init__('c', "")