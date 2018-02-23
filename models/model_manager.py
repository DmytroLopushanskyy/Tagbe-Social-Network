# -*- coding:utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session
import sqlite3
from schematics.models import Model
from models.models import UserModel, UserAddModel, UserType, GroupUserModel
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL

conn = sqlite3.connect('database.sqlite3', check_same_thread=False)

class UserManager():
    user_type = UserType()
    group_type = GroupUserModel()
    user_type.id = 1
    user_type.type_name = 'user'
    load_models = {}

    def __init__(self):
        self.user = UserModel()

    def empty(self):
        self.user.add = 123
        return self.user

    def getGroupModelFromForm(self,data, email):
        self.user.first_name = data['f_name']
        self.user.last_name = data['l_name']
        self.user.about = data['about']
        self.user.type = self.user_type
        self.user.email = email
        #self.user.validate()
        return self

    def getModelFromForm(self,form):
        self.user.first_name = form.get('f_name', '')
        self.user.last_name = form.get('l_name', '')
        self.user.type = self.user_type
        self.user.user_photo = 'default-user-image.png, default-background.png'
        self.user.email = form.get('email', '')
        self.user.password = form.get('pwd', '')
        #self.user.validate()
        return self

    def getDataFromEditAdd(self,form):
        self.user.add = UserAddModel()
        self.user.add.age = form.get('age', '')
        self.user.add.phone = form.get('phone', '')
        self.user.add.address = form.get('address', '')
        self.user.add.sex = form.get('sex', '')
        #self.user.add.validate()
        return self.user.add

    def check_user(self):
        sql = 'SELECT * FROM users WHERE email = "{}"'.format(self.user.email)
        check_user = executeSelectOne(sql)
        if check_user:
            return True
        return False


    def addNewUser(self):
        curs = conn.cursor()
        curs.execute("INSERT INTO users ('first_name', 'last_name', 'type', 'user_photo', 'descr', 'email', 'password', 'create_time')  VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')" \
            .format(self.user.first_name, self.user.last_name, self.user_type, self.user.user_photo, self.user.descr, self.user.email, self.user.password, self.user.create_time))
        conn.commit()

        curs.execute("select id from users where email = '{}'".format(self.user.email))
        data = curs.fetchone()
        #user = UserManager.selectUser(UserManager(), data)
        curs.execute("INSERT INTO users_add ('age', 'create_time', 'phone', 'address', 'sex', 'user')  VALUES ('{}','{}','{}','{}','{}', '{}')" \
            .format('No info', self.user.create_time, 'No info', 'No info', 'No info', data[0]))
        conn.commit()
        return

    def addNewGroup(self):
        curs = conn.cursor()
        curs.execute("INSERT INTO users ('first_name', 'last_name', 'type', 'user_photo', 'descr', 'email', 'password', 'create_time')  VALUES ('{}','{}','{}','{}','{}','{}','{}','{}')" \
            .format(self.user.first_name, self.user.last_name, self.user_type, 'default-user-image.png, default-background.png', self.user.about, self.user.email, 'group_type', self.user.create_time))
        conn.commit()

        curs.execute("select id from users where email = '{}' and password = 'group_type' and create_time = '{}' and first_name = '{}' and last_name = '{}' and descr = '{}'".format(self.user.email, self.user.create_time, self.user.first_name, self.user.last_name, self.user.about))
        data = curs.fetchone()
        #user = UserManager.selectUser(UserManager(), data)
        curs.execute("INSERT INTO users_add ('age', 'create_time', 'phone', 'address', 'sex', 'user')  VALUES ('{}','{}','{}','{}','{}', '{}')" \
            .format('No info', self.user.create_time, 'No info', 'No info', '0', data[0]))
        conn.commit()
        return data[0]

    def selectUser(self,data=[]):
        self.user.id = data[0]
        self.user.first_name = data[1]
        self.user.last_name = data[2]
        self.user.type = data[3]
        self.user.email = data[7]
        self.user.password = data[8]
        self.user.create_time = data[9]
        self.user.descr = data[4]
        self.user.user_photo = data[5]
        curs = conn.cursor()
        curs.execute("select * from users_add where user = '{}'".format(self.user.id))
        data = curs.fetchone()
        self.user.add = UserManager._selectUserAdd(UserManager(), data)
        return self.user



    def _selectUserAdd(self, data=[]):
        self.user.age = data[1]
        self.user.create_time = data[2]
        self.user.phone = data[3]
        self.user.address = data[4]
        self.user.sex = data[5]
        return self.user




    def loginUser(self,lofin_form):
        email = lofin_form.get('email', '')
        password = lofin_form.get('passw', '')
        sql = 'select * from users where email = "{}" and password = "{}"'.format(email, password)
        user = executeSelectOne(sql)
        # print(user)
        if user:
            self.selectUser(user)
            self.load_models[self.user.nickname] = self.user
            # print(self.user)
            return True
        return False

    def toDict(self):
        def recurs(model):
            result = {}
            items = model.items()
            for it in items:
                if isinstance(it[1], Model):
                    result[it[0]] = recurs(it[1])
                result[it[0]] = it[1]
            return result
        return recurs(self.user)


if __name__ == '__main__':
    manager = UserManager()
    manager.user.id = 1
    manager.selectUser()
    print(manager.toDict())


