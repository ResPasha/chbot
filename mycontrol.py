import model
import control
import strings
from db_helper import DBHelper

db = DBHelper()


class UserControl(control.Control):
    def __init__(self, user_id):
        user = db.usr.get_by_id(user_id)
        assert isinstance(user, model.User)
        super().__init__(strings.cmd_user + str(user_id))
        self.user = user

    def _get_inline_kb(self, *args):
        pass

    def _process(self, data):
        pass

    def _get_caption(self, *args):
        pass

    def _get_text(self, *args):
        s = strings.cmd_user + str(self.user.id) + '\n\n'
        s += strings.msg_first_name + self.user.first_name + '\n'
        s += strings.msg_last_name + self.user.last_name + '\n'
        s += strings.msg_username + self.user.username
        return s


class StartMenu(control.Menu):
    def __init__(self):
        super().__init__(strings.cmd_start, [
            (strings.btn_intro, strings.msg_intro),
            (strings.btn_help, strings.msg_help),
            (strings.btn_info, strings.msg_info)
        ])


class UserListControl(control.Pager):
    def __init__(self):
        super().__init__(strings.cmd_users, db.usr.get_all())
        self.title = strings.msg_users + '\n'

    @staticmethod
    def _get_item_text(item):
        s = item.first_name + ' @' + item.username
        s += '\n/' + strings.cmd_user + str(item.id) + '\n'
        return s


class ErrControl(control.Control):
    def __init__(self):
        super().__init__(strings.cmd_error)

    def _get_inline_kb(self, *args):
        pass

    def _process(self, data):
        pass

    def _get_caption(self, *args):
        pass

    def _get_text(self, *args):
        return strings.errmsg_unknown_cmd
