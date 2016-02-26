class Image:
    res = None
    file_id = None
    db_id = None
    extra_tags = []

    def __init__(self, hires_link, copyright_tag):
        # TODO update constructor for better integration with db
        self.hires_link = hires_link
        self.copyright_tag = copyright_tag


class User:
    id = None
    fname = None
    lname = None
    uname = None
    type = None
    last_msg = None

    def __init__(self, user=None, msg=None):
        if user or msg:
            if not user:
                user = msg['from']
            self.id = user['id']
            self.fname = user['first_name']
            if 'last_name' in user:
                self.lname = user['last_name']
            if 'username' in user:
                self.uname = user['username']
            if msg:
                self.last_msg = msg['message_id']
