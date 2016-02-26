from pymongo import MongoClient
from bson.objectid import ObjectId
from models import *
import config

res_tag_720 = '#720p'
res_tag_1080 = '#1080p'
res_tag_1920 = '#1920p'
res_tag_wide = '#wide'
res_tag_vert = '#verticalhd'

id_field = '_id'

cr_coll_name = 'cr_tags'
cr_orig_field = 'original'
cr_repl_field = 'replacement'

img_coll_name = 'not_posted_yet'
img_hires_field = 'hires_link'
img_cr_field = 'cr_tag'
img_res_field = 'res'
img_fileid_field = 'photo'
img_extras_field = 'extra_tags'

usr_coll_name = 'users'
usr_id_field = 'uid'
usr_fname_field = 'first_name'
usr_lname_field = 'last_name'
usr_uname_field = 'username'
usr_type_field = 'utype'
usr_lastmsg_field = 'last_msg'

nsfw_postfix = '_nsfw'


class DBHelper:
    def __init__(self):
        db_client = MongoClient(config.db_auth)
        db = db_client[config.db_name]

        if cr_coll_name not in db.collection_names():
            db.create_collection(cr_coll_name)
        self.cr_coll = db[cr_coll_name]

        if img_coll_name not in db.collection_names():
            db.create_collection(img_coll_name)
        self.img_coll = db[img_coll_name]

        if usr_coll_name not in db.collection_names():
            db.collection_names(usr_coll_name)
        self.usr_coll = db[usr_coll_name]

    @staticmethod
    def get_res_tags(res):
        res_x = int(res[0])
        res_y = int(res[1])
        res_tags = []
        if res_x > res_y:
            if res_y > 1920:
                res_tags.append(res_tag_1920)
            if res_y > 1080:
                res_tags.append(res_tag_1080)
            elif res_y > 720:
                res_tags.append(res_tag_720)
            if res_x > 3 * res_y:
                res_tags.append(res_tag_wide)
        elif res_y > 1000:
            res_tags.append(res_tag_vert)
        return res_tags

    def get_cr_htag(self, cr_tag):
        found = self.cr_coll.find_one({cr_orig_field: cr_tag})
        if found:
            return found[cr_repl_field]
        else:
            return cr_tag

    def get_image(self, db_id):
        db_doc = self.img_coll.find_one({id_field: ObjectId(db_id)})
        image = Image(db_doc[img_hires_field], db_doc[img_cr_field])
        image.copyright_tag = self.get_cr_htag(image.copyright_tag)
        image.res = db_doc[img_res_field]
        if db_doc[img_extras_field]:
            image.extra_tags = db_doc[img_extras_field]
        image.db_id = db_id
        image.file_id = db_doc[img_fileid_field]
        return image

    def get_caption(self, image):
        tags = []
        tags.extend(self.get_res_tags(image.res))
        image.copyright_tag = self.get_cr_htag(image.copyright_tag)
        tags.append(image.copyright_tag)
        if image.extra_tags:
            tags.extend(image.extra_tags)
        return image.hires_link + '\n' + ' '.join(tags)

    def get_nsfw_caption(self, image):
        tags = []
        tags.extend(self.get_res_tags(image.res))
        image.copyright_tag = self.get_cr_htag(image.copyright_tag)
        tags.append(image.copyright_tag)
        if image.extra_tags:
            tags.extend(image.extra_tags)
        nsfw_tags = [tag + nsfw_postfix for tag in tags if tag and tag.strip()]
        return image.hires_link + '\n' + ' '.join(nsfw_tags)

    def add(self, image):
        image.db_id = self.img_coll.insert_one({
            img_hires_field: image.hires_link,
            img_res_field: image.res,
            img_cr_field: image.copyright_tag,
            img_fileid_field: image.file_id,
            img_extras_field: image.extra_tags
        }).inserted_id

    def update(self, image):
        self.img_coll.update_one(
            {id_field: ObjectId(image.db_id)},
            {'$set': {
                img_hires_field: image.hires_link,
                img_res_field: image.res,
                img_cr_field: image.copyright_tag,
                img_fileid_field: image.file_id,
                img_extras_field: image.extra_tags
            }}
        )
        pass

    def add_cr_rule(self, new_cr, cr):
        db_upd_result = self.cr_coll.update_many(
            {'$or': [{cr_orig_field: cr}, {cr_repl_field: cr}]},
            {'$set': {cr_repl_field: new_cr}}
        )
        if db_upd_result.modified_count == 0:
            self.cr_coll.insert_one({cr_orig_field: cr, cr_repl_field: new_cr})

    def find_by_link(self, hires_link):
        db_rec = self.img_coll.find_one({img_hires_field: hires_link})
        if not db_rec:
            return None
        image = Image(db_rec[img_hires_field], db_rec[img_cr_field])
        image.file_id = db_rec[img_fileid_field]
        image.res = db_rec[img_res_field]
        if db_rec[img_extras_field]:
            image.extra_tags = db_rec[img_extras_field]
        image.db_id = db_rec[id_field]
        return image

    def delete(self, image):
        self.img_coll.delete_one({id_field: ObjectId(image.db_id)})

    def add_usr(self, user):
        db_rec = self.usr_coll.find_one({usr_id_field: user.id})
        if db_rec:
            user.type = db_rec[usr_type_field]
            self.usr_coll.update_one(
                {usr_id_field: user.id},
                {'$set': {
                    usr_fname_field: user.fname,
                    usr_lname_field: user.lname,
                    usr_uname_field: user.uname,
                    usr_lastmsg_field: user.last_msg
                }}
            )
        else:
            user.type = 'user'
            self.usr_coll.insert_one({
                usr_id_field: user.id,
                usr_fname_field: user.fname,
                usr_lname_field: user.lname,
                usr_uname_field: user.uname,
                usr_lastmsg_field: user.last_msg,
                usr_type_field: 'user'
            })

    def update_usr_type(self, user):
        self.usr_coll.update_one(
            {usr_id_field: user.id},
            {'$set': {
                usr_type_field: user.type
            }}
        )

    def del_usr(self, user):
        self.usr_coll.delete_one({usr_id_field: user.id})

    def get_images(self):
        for db_doc in self.img_coll.find({}):
            image = Image(db_doc[img_hires_field], db_doc[img_cr_field])
            image.copyright_tag = self.get_cr_htag(image.copyright_tag)
            image.res = db_doc[img_res_field]
            if db_doc[img_extras_field]:
                image.extra_tags = db_doc[img_extras_field]
            image.db_id = db_doc[id_field]
            image.file_id = db_doc[img_fileid_field]
            yield image

    def get_users(self):
        for doc in self.usr_coll.find({}):
            user = User()
            user.id = doc[usr_id_field]
            user.fname = doc[usr_fname_field]
            user.lname = doc[usr_lname_field]
            user.uname = doc[usr_uname_field]
            user.type = doc[usr_type_field]
            user.last_msg = doc[usr_lastmsg_field]
            yield user
