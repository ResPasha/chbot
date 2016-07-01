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
        self.last_name = kwargs['last_name']
        self.username = kwargs['username']

    def __str__(self):
        s = self.first_name + ' @' + self.username
        s += '\n/user' + str(self.id)
        return s

    def update(self, data):
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.username = data.username
