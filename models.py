import telepot.namedtuple


class ModelObj:
    def __init__(self, d):
        self.__dict__.update(d)

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        return str(self.__dict__)


class User(ModelObj, telepot.namedtuple.User):
    def __init__(self, **kwargs):
        d = {}
        d.update(kwargs)
        if 'id' in d:
            del d['id']
            d['_id'] = kwargs['id']
        super().__init__(d)

    def __str__(self):
        s = self.first_name + ' @' + self.username
        s += '\n/user' + str(self._id)
        return s
