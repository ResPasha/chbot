from pymongo import MongoClient
from bson.objectid import ObjectId
from model import *
import config


def singleton(class_):
    instances = {}

    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance


@singleton
class DBHelper:
    def __init__(self):
        db_client = MongoClient(config.db_auth)
        self.db = db_client[config.db_name]

        usr_coll_name = 'usr'
        if usr_coll_name not in self.db.collection_names():
            self.db.create_collection(usr_coll_name)
        self.usr = UserDAO(self.db[usr_coll_name])


class DAO:
    def __init__(self, coll):
        self.coll = coll

    def get_all(self):
        raise NotImplementedError()

    def get_by_id(self, item_id):
        raise NotImplementedError()

    def update(self, item):
        raise NotImplementedError()

    def delete(self, item_id):
        raise NotImplementedError()

    def create(self, item):
        raise NotImplementedError()


class UserDAO(DAO):
    def get_by_id(self, item_id):
        db_rec = self.coll.find_one({'_id': int(item_id)})
        return User(**db_rec)

    def get_all(self):
        return [User(**db_rec) for db_rec in self.coll.find({})]

    def update(self, item):
        self.coll.update_one({'_id': item.id}, {'$set': item.to_dict()})

    def delete(self, item_id):
        self.coll.delete_one({'_id': item_id})

    def create(self, item):
        self.coll.insert_one(item.to_dict())
