from collections import namedtuple
import traceback

from telepot.namedtuple import InlineKeyboardButton, InlineKeyboardMarkup
from telepot.exception import TelegramError

from bot import Bot
import strings

ProcessResult = namedtuple('ProcessResult', [
                               'answer_text',
                               'show_alert',
                               'to_update'
                           ])
UPDATE_TEXT = 0
UPDATE_CAPTION = 1
UPDATE_REPLY_MARKUP = 2


class Control:
    def __init__(self, name):
        self.bot = Bot(None)
        self.name = name

    def process(self, query):
        assert query.data.startswith(self.name)
        user = query.from_
        if query.message:
            msg_identifier = (str(user.id), str(query.message.message_id))
        else:
            msg_identifier = str(query.inline_message_id)
        data = query.data.split('#')[1]

        if not data:
            self.bot.answerCallbackQuery(query.id, '', '')
            return

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
        except TelegramError as e:
            if e.args[0] != 'Bad Request: message is not modified':
                traceback.print_exc()
                raise e

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
            new_kb = []
            for row in kb:
                new_row = []
                for b in row:
                    assert isinstance(b, InlineKeyboardButton)
                    new_b = InlineKeyboardButton(
                        text=b.text,
                        url=b.url,
                        callback_data=self.name + '#' + b.callback_data,
                        switch_inline_query=b.switch_inline_query
                    )
                    new_row.append(new_b)
                new_kb.append(new_row)
            return InlineKeyboardMarkup(inline_keyboard=new_kb)
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
    def __init__(self, name, source_list):
        super().__init__(name)
        self.list = source_list
        self.items_per_page = 3
        self.buttons_count = 5
        self.title = ""
        self.default_page_no = 1

    def _get_text(self, data=None):
        page_no = int(data) if data else self.default_page_no
        text = self.title + '\n'
        left = (page_no - 1) * self.items_per_page
        right = left + self.items_per_page
        for item in self.list[left:right]:
            # TODO: check if builtin
            text += self._get_item_text(item) + '\n'
        return text

    @staticmethod
    def _get_item_text(item):
        raise NotImplementedError

    def _get_inline_kb(self, data=None):
        marks = ['« ', '< ', '·', ' >', ' »', ' - ']
        page_no = int(data) if data else self.default_page_no
        buttons = {}

        pages_count = len(self.list) // self.items_per_page
        if len(self.list) % self.items_per_page > 0:
            pages_count += 1

        left = page_no - (self.buttons_count // 2)
        right = page_no + (self.buttons_count // 2)
        if pages_count >= self.buttons_count:
            if left < 1:
                left = 1
            if left == 1:
                right = self.buttons_count
            if right > pages_count:
                right = pages_count
            if right == pages_count:
                left = pages_count - self.buttons_count + 1

        for i in range(left, right + 1):
            if 0 < i <= pages_count:
                if i < page_no:
                    buttons[i] = marks[1] + str(i)
                if i == page_no:
                    buttons[i] = marks[2] + str(i) + marks[2]
                if i > page_no:
                    buttons[i] = str(i) + marks[3]
            else:
                buttons[i] = marks[5]

        if buttons[left].startswith(marks[1]):
            del buttons[left]
            buttons[1] = marks[0] + '1'
        if buttons[right].endswith(marks[3]):
            del buttons[right]
            buttons[pages_count] = str(pages_count) + marks[4]

        button_row = [
            InlineKeyboardButton(
                text=buttons[key],
                callback_data=str(key) if buttons[key] != marks[5] else ''
            ) for key in sorted(buttons.keys())
            ]
        return [button_row]

    def _process(self, data):
        if data:
            return ProcessResult(strings.ca_done, False, UPDATE_TEXT)

    def _get_caption(self, *args):
        pass


class Menu(Control):
    Item = namedtuple('Item',
                      [
                          'command',
                          'cb_text',
                          'out_text'
                      ])

    def __init__(self, name, menu_dict):
        super().__init__(name)
        i = 0
        self.items = []
        for item in menu_dict:
            self.items.append(Menu.Item(str(i), item[0], item[1]))
            i += 1
        self.title = ''

    def _get_caption(self, *args):
        pass

    def _get_inline_kb(self, data=None):
        if not data:
            data = '0'
        button_row = []
        for item in self.items:
            text = item.cb_text
            if data == item.command:
                text = '* ' + text
            button_row.append(InlineKeyboardButton(text=text, callback_data=item.command))
        return [button_row]

    def _get_text(self, data=None):
        if not data:
            data = '0'
        return self.items[int(data)].out_text

    def _process(self, data):
        if data:
            return ProcessResult(self.items[int(data)].cb_text, False, UPDATE_TEXT)


class Like(Control):  # TODO: behave like @like bot
    pass
