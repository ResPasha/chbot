import model
import control
from db_helper import DBHelper

db = DBHelper()


class UserControl(control.Control):
    def __init__(self, user_id):
        user = db.usr.get_by_id(user_id)
        assert isinstance(user, model.User)
        super().__init__('user' + str(user_id))
        self.user = user

    def _get_inline_kb(self, *args):
        pass

    def _process(self, data):
        pass

    def _get_caption(self, *args):
        pass

    def _get_text(self, *args):
        s = 'user' + str(self.user.id) + '\n'
        s += 'First name: ' + self.user.first_name + '\n'
        s += 'Last name: ' + self.user.last_name + '\n'
        s += 'Username: @' + self.user.username
        # s += '\n/user' + str(self.user.id)
        return s


class StartMenu(control.Menu):
    def __init__(self):
        super().__init__('start', [
            ('Intro', 'Hello there!'),
            ('Help', 'Little help'),
            ('Info', 'Source code, author and contact info')
        ])


class UserListControl(control.Pager):
    def __init__(self):
        super().__init__('users', db.usr.get_all())
        self.title = 'Users list:\n'

    @staticmethod
    def _get_item_text(item):
        s = item.first_name + ' @' + item.username
        s += '\n/user' + str(item.id) + '\n'
        return s
