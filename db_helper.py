from pymongo import MongoClient
from bson.objectid import ObjectId
from models import ModelObj
import config

def singleton(class_):
    instances = {}
    def getinstance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return getinstance

@singleton
class DBHelper:
    def __init__(self):
        db_client = MongoClient(config.db_auth)
        self.db = db_client[config.db_name]

        usr_coll_name = 'usr'
        if usr_coll_name not in self.db.collection_names():
            self.db.create_collection(usr_coll_name)
        self.usr = self.db[usr_coll_name]

    @staticmethod
    def sync(coll, item):
        def remove_id(d):
            r = dict(d)
            del r['_id']
            return r

        db_rec = coll.find_one({'_id': item._id})
        if db_rec:
            for key in db_rec.keys():  # FIXME
                if (key not in item.__dict__) \
                        or (not item.__dict__[key]):
                    item.__dict__[key] = db_rec[key]
            coll.update_one(
                {'_id': item._id},
                {'$set': remove_id(item.__dict__)}
            )
        else:
            coll.insert_one(item.__dict__)

    @staticmethod
    def rm(coll, item):
        coll.delete_one({'_id': item._id})

    @staticmethod
    def get(coll, type):
        assert issubclass(type, ModelObj)
        items = []
        for db_rec in coll.find({}):
            items.append(type(**db_rec))
        return items