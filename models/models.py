# -*- coding:utf-8 -*-

from schematics.models import Model
from schematics.types import StringType, EmailType, BooleanType, IntType, ListType, ModelType, DateTimeType
from datetime import datetime


class UserType(Model):
    _name = 'user_type'
    id = IntType(required=False)
    type_name = StringType(required=True)
    create_time = DateTimeType(required=True, default=datetime.now())

class UserAddModel(Model):
    _name = 'user_add'
    id = IntType(required=False)
    age = IntType(default=None, required=False)
    create_time = DateTimeType(required=True, default=datetime.now())
    phone = StringType(default=None, required=False)
    address = StringType(default=None, required=False)
    sex = IntType(default=None, required=False)


class UserModel(Model):
    _name = 'users'
    id = IntType(required=False)
    first_name = StringType(required=True)
    last_name = StringType(required=False, default='')
    type = StringType(required=False, default='') #ModelType(UserType, required=True)
    descr = StringType(required=False, default='')
    user_photo = StringType(required=False, default='default-user-image.png, default-background.png')
    user_photos = ListType(StringType, required=False, default=[])
    email = EmailType(required=True)
    password = StringType(required=True)
    create_time = DateTimeType(required=True, default=datetime.now())
    user_add = ModelType(UserAddModel)






class GroupUserModel(Model):
    id = IntType(required=False)
    group = ModelType(UserModel, required=True)
    user = ModelType(UserModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())


class PostModel(Model):
    id = IntType(required=False)
    user_id = IntType(required=True)
    images = StringType(required=False, default='')
    text = StringType(required=False, default=None)
    tags = StringType(required=False, default=None)
    location = StringType(required=False, default=None)
    date = DateTimeType(required=True, default=datetime.now())


class CommentsModel(Model):
    id = IntType(required=False)
    text = StringType(required=False, default=None)
    likes = IntType(required=True, default=0)
    user = ModelType(UserModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())


class PostCommentModel(Model):
    id = IntType(required=False)
    post = ModelType(PostModel, required=True)
    comment = ModelType(CommentsModel, required=True)
    create_time = DateTimeType(required=True, default=datetime.now())


class MessageModel(Model):
    id = IntType(required=False)
    user_from = ModelType(UserModel, required=True)
    user_to = ModelType(UserModel, required=True)
    is_read = BooleanType(required=True, default=False)
    create_time = DateTimeType(required=True, default=datetime.now())


if __name__ == '__main__':
    type = UserType()
    type.id = 1
    type.name = 'test'

    user = UserModel()
    user.id = 1
    user.first_name = 'test'
    user.last_name = 'test'
    user.type = type
    user.descr = 'test'
    user.user_photo = 'test'
    user.user_photos = ['test']
    user.email = 'testtest.test'
    user.nickname = 'test'
    user.password = 'test'

    print(user.items())
    print(user.validate())
