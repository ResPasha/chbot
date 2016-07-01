import telepot.namedtuple


class ModelObj:
    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        pass  # TODO: implement


class User(ModelObj):
    def __init__(self, **kwargs):
        self.id = kwargs['_id']
        self.first_name = kwargs['first_name']
        self.last_name = kwargs.get('last_name')
        self.username = kwargs.get('username')
        self.type = kwargs['type'] if kwargs.get('type') else 'sender'
        self.log = kwargs['log'] if kwargs.get('log') else None  # TODO: and usertype
        self.l_subs = kwargs['l_subs'] if kwargs.get('l_subs') else None  # TODO: and usertype

    def __str__(self):
        s = self.first_name + ' @' + self.username
        s += '\n/user' + str(self.id)
        return s

    def update(self, data):
        assert self.id == data.id
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.username = data.username
