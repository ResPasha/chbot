class Model:
    def __repr__(self):
        return str(self.__dict__)

    def to_dict(self):
        d = {}
        for k, v in vars(self).items():
            if isinstance(v, Model):
                d[k] = v.to_dict()
            elif not str(k).startswith('_'):
                if str(k) == 'id':
                    k = '_id'
                d[k] = v
        return d


class User(Model):
    def __init__(self, **kwargs):
        self.id = kwargs.get('_id') or kwargs.get('id')
        self.first_name = kwargs['first_name']
        self.last_name = kwargs.get('last_name')
        self.username = kwargs.get('username')
        self.type = kwargs['type'] if kwargs.get('type') else 'sender'
        self.log = kwargs['log'] if kwargs.get('log') else None  # TODO: and usertype
        self.l_subs = kwargs['l_subs'] if kwargs.get('l_subs') else None  # TODO: and usertype

    def update(self, data):
        assert self.id == data.id
        self.first_name = data.first_name
        self.last_name = data.last_name
        self.username = data.username
