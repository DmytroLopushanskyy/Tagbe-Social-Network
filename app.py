# -*-coding: utf-8 -*-
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
from models.executeSqlite3 import executeSelectOne, executeSelectAll, executeSQL
from functools import wraps
from models.model_manager import UserManager
import os
from os import listdir
from os.path import isfile, join
import schematics
#from schematics.models import Model
import jinja2
#import simplejson as json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)
app.secret_key = 'super secret key'
#someone.html
conn = sqlite3.connect('database.sqlite3', check_same_thread=False)
#curs = conn.cursor()
#curs.execute('''CREATE TABLE `users` (`id`	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,`f_name`	TEXT NOT NULL,`l_name`	TEXT NOT NULL, `email`	TEXT NOT NULL, `password`	TEXT NOT NULL);''')

def sessionCheck():
    try:
        if session['email']:
            curs = conn.cursor()
            user_model = user_info(curs, session['email'])
            session['username'] = user_model.first_name + ' ' + user_model.last_name
            notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
            notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
            if not notifications:
                notifications = []
            else:
                notifications_id = notifications_id[0].split(',')

            context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
            return render_template('profile.html', **context2)
    except KeyError:
        none = 'none'
        nothing = UserManager().empty()
        context = {'block': none, 'd_none': 'block', 'user': nothing, 'length': 0}
        return render_template('landing.html', **context)

@app.route('/', methods=['GET'])
def return_home():
    return sessionCheck()


def sql_to_string(row):
    row = ' '.join(str(x) for x in row)
    return row


def user_info(curs, email):
    if email.split(' ')[0] == 'group':
        curs.execute("select * from users where id = '{}'".format(email.split(' ')[1]))
        data = curs.fetchone()
        user = UserManager.selectUser(UserManager(), data)
        return user
    else:
        curs.execute("select * from users where email = '{}'".format(email))
        data = curs.fetchone()
        user = UserManager.selectUser(UserManager(), data)
        return user




@app.route('/', methods=['POST'])
def validation():
    #session validation
    try:
        if session['email']:
            curs = conn.cursor()
            full_name = user_info(curs, session['email'])
            notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(full_name.id)).fetchall()
            notifications_id = curs.execute("select notifications from users where id = '{}'".format(full_name.id)).fetchone()
            if notifications_id[0] is None:
                notifications = []
            else:
                notifications_id = notifications_id[0].split(',')
            context2 = {'block': 'block', 'd_none': 'none', 'user': full_name, 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
            return render_template('profile.html', **context2)
    except KeyError:
        #if user is not in session
        var1 = request.form['email']
        var2 = request.form['pwd']
        if var1 == '' or var2 == '':
            return redirect(url_for('login'))
        else:
            curs = conn.cursor()
            user_email = request.form['email']
            password = request.form['pwd']
            print(user_email, password)
            if curs.execute("select 1 from users where email = '{}' and password = '{}'".format(user_email, password)).fetchone() == None:
                return render_template('error.html')
            else:
                full_name = user_info(curs, email = user_email)
                notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(full_name.id)).fetchall()
                notifications_id = curs.execute("select notifications from users where id = '{}'".format(full_name.id)).fetchone()
                if notifications_id[0] == None:
                    notifications = []
                    print('none')
                else:
                    notifications_id = notifications_id[0].split(',')
                context2 = {'block': 'block', 'd_none': 'none', 'user': full_name, 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}

                curs.execute("select 1 from users where email = '{}' and password = '{}'".format(user_email, password))
                data = curs.fetchone()

                session['email'] = user_email
                return render_template('profile.html', **context2)
            #endif user is in session



def session_checking():
    try:
        if session['email']:
            return True
    except KeyError:
        return False


@app.route('/signup', methods=['GET'])
def signup():
    if session_checking():
        return redirect(url_for('return_home'))
    else:
        return render_template('signup.html')

def addToSession(user):
    session['email'] = user.user.email

@app.route('/signup', methods=['POST'])
def registration():
    try:
        if session['email']:
            session_checking = True
    except KeyError:
        session_checking = False


    if session_checking:
        curs = conn.cursor()

        f_name = request.json['name']
        l_name = request.json['description']
        about = request.json['location']
        id = curs.execute("select id from users where email = '{}'".format(session['email'])).fetchone()

        data = {'f_name': f_name, 'l_name': l_name, 'about': about}
        try:
            user = UserManager().getGroupModelFromForm(data, id[0])

        except schematics.exceptions.DataError:
            context = {'errors': 'Wrong Data'}
            return render_template('signup.html', **context)

        group_id = user.addNewGroup()
        curs = conn.cursor()
        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model,  'messages': 'Group successfully created! You can manage it on group page', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'id': group_id })
    else:
        curs = conn.cursor()
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        reg_email = request.form['email']
        reg_pass = request.form['pwd']
        try:
            user = UserManager().getModelFromForm(request.form)
        except schematics.exceptions.DataError:
            context = {'errors': 'Wrong Data'}
            return render_template('signup.html', **context)

        val = curs.execute("select 1 from users where email = '{}'".format(reg_email)).fetchone()

        if val:
            context = {'errors': 'User with this Email already exists!!!'}
            return render_template('signup.html', **context)
        else:
            user.addNewUser()
            addToSession(user)
            curs = conn.cursor()
            user_model = user_info(curs, session['email'])
            notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
            notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
            if notifications_id[0] == None:
                notifications = []
                print('none')
            else:
                notifications_id = notifications_id[0].split(',')
            context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
            return render_template('profile.html', **context2)

@app.route('/group_edit', methods=['GET'])
def group_edit():
    curs = conn.cursor()
    id = request.args.get('id')
    group_data = curs.execute("select * from users where id = '{}'".format(id)).fetchone()
    if session:
        current_email = session['email']
        current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
        if int(current_id[0]) == int(group_data[7]):
            data = 'group ' + str(id)
            user_model = user_info(curs, data)
            context = {'errors': '', 'user': user_model, 'ifgroup': True}
            return render_template('add_info_edit.html', **context)
        else:
            return redirect(url_for('return_home'))
    else:
        return redirect(url_for('return_home'))


@app.route('/add_edit', methods=['GET'])
def add_edit():
    try:
        if session['email']:
            curs = conn.cursor()

            user_model = user_info(curs, session['email'])
            context = {'errors': '', 'user': user_model}
            return render_template('add_info_edit.html', **context)
    except KeyError:
        return redirect(url_for('return_home'))


@app.route('/add_edit', methods=['POST'])
def add_edit_validation():
    curs = conn.cursor()
    if session:
        print(request.json)
        data = 'group ' + str(request.json['id'])
        user_model = user_info(curs, data)
        print(user_model)

        new_first_name = request.json['f_name']
        new_last_name = request.json['l_name']
        try:
            new_password = request.json['new_pass']
            local = True
        except KeyError:
            new_password = user_model.password
            new_email = None
            descr = request.json['descr']
            age = user_model.add.age
            phone = user_model.add.phone
            address = user_model.add.address
            sex = user_model.add.sex
            local = False
            id = request.json['id']

        if local:
            descr = user_model.descr
            new_email = request.json['new_email']
            age = request.json['age']
            phone = request.json['phone']
            address = request.json['address']
            sex = request.json['sex']
            id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]

        try:
            if new_email:
                first = curs.execute("SELECT id from users WHERE email ='{}'".format(new_email)).fetchall()[0][0]
                new_email = session['email']

                error = "Email hasn't been changed because it already exists"
                context2 = {'errors': error, 'user': user_model}
                return render_template('add_info_edit.html', **context2)
            else:
                if local:
                    new_email = session['email']
                else:
                    new_email= user_model.email
        except IndexError:
            print(True)
            new_email = request.json['new_email']
            #session['email'] = new_email
        print('happy', new_password, new_email, descr, age, phone, address, sex)
        try:
            user_add = UserManager().getDataFromEditAdd(request.form)
        except schematics.exceptions.DataError:
            context = {'errors': 'Wrong Data'}
            return render_template('add_info_edit.html', **context)

        curs.execute("UPDATE users_add SET age = '{}', phone = '{}', address = '{}', sex = '{}' WHERE user ='{}'".format(age, phone, address, sex, id)).fetchone()

        curs.execute("UPDATE users SET first_name = '{}', last_name = '{}', descr = '{}', password = '{}', email = '{}' WHERE id ='{}'".format(new_first_name, new_last_name, descr, new_password, new_email, id)).fetchone()

        conn.commit()

        #del session['email'] = new_email
        if local:
            session['email'] = new_email

        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        return jsonify({'status': 'changed!'})
    else:
        return redirect(url_for('return_home'))



@app.route('/login')
def login():
    try:
        if session['email']:
            return redirect(url_for('return_home'))
    except KeyError:
        return render_template('login.html')


@app.route('/logout')
def logout():
    try:
        del session['email']
        return render_template('landing.html')
    except KeyError:
        return redirect(url_for('return_home'))

@app.route('/user/<username>')
def user_search(username):
    try:
        username = username.split(' ')

        curs = conn.cursor()
        friend = curs.execute("select * from users where first_name = '{}' and last_name = '{}'".format(username[0], username[1])).fetchall()
        if not friend:
            user_model = user_info(curs, session['email'])
            context3 = {'user': user_model, 'name': '', 'email': 'nothing_found', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': friend, 'block': 'none'}
            return render_template('friends.html', **context3)
        if len(friend)>1:
            user_model = user_info(curs, session['email'])
            context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': friend, 'block': 'none'}
            return render_template('friends.html', **context3)
        else:
            friend = friend[0]

            friend_add = curs.execute("select * from users_add where user = '{}'".format(friend[0])).fetchone()
            if session:
                current_email = session['email']
                current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
                f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()
                s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(friend[0], current_id[0])).fetchone()
                print(f_col, s_col)
                if f_col:
                    if_blocked = curs.execute("select block from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()
                    sender_id = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()[0]
                elif s_col:
                    if_blocked = curs.execute("select block from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()
                    sender_id = curs.execute("select sender_id from name where user2_id = '{}' and user1_id = '{}'".format(current_id[0], friend[0])).fetchone()[0]
                else:
                    if_blocked = [None]
                    sender_id = None
            else:
                current_id=None
                if_blocked = [None]
                sender_id = None
            Boulean = FriendConnectionValidation(curs, friend_add, current_id)

            user_model = user_info(curs, session['email'])
            context3 = {'user': user_model, 'name': friend[1] + ' ' + friend[2],'friend': friend, 'email': friend[7], 'age': friend_add[1], 'phone': friend_add[3], 'sex': friend_add[5], 'address': friend_add[4], 'id': friend_add[6], 'friends': Boulean, 'if_blocked': if_blocked[0], 'sender_id': sender_id, 'current_id': str(current_id[0])}
            return render_template('someone.html', **context3)
    except (TypeError):
        return render_template('error.html')

@app.route('/special')
def special_user_search():
        curs = conn.cursor()
        id = request.args.get('id')
        friend = curs.execute("select * from users where id = '{}'".format(id)).fetchone()
        friend_add = curs.execute("select * from users_add where user = '{}'".format(id)).fetchone()
        if session:
            current_email = session['email']
            current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
            f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()
            s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(friend[0], current_id[0])).fetchone()
            print(f_col, s_col)
            print(current_id[0], friend[0])
            if f_col:
                if_blocked = curs.execute("select block from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()
                sender_id = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend[0])).fetchone()[0]
            elif s_col:
                if_blocked = curs.execute("select block from name where user2_id = '{}' and user1_id = '{}'".format(current_id[0], friend[0])).fetchone()
                sender_id = curs.execute("select sender_id from name where user2_id = '{}' and user1_id = '{}'".format(current_id[0], friend[0])).fetchone()[0]
            else:
                if_blocked = [None]
                sender_id = None
        else:
            current_id=None
            if_blocked = [None]
            sender_id = None

        Boulean = FriendConnectionValidation(curs, friend_add, current_id)

        user_model = user_info(curs, session['email'])
        context3 = {'user': user_model, 'name': friend[1] + ' ' + friend[2], 'email': friend[7], 'friend': friend, 'age': friend_add[1], 'phone': friend_add[3], 'sex': friend_add[5], 'address': friend_add[4], 'id': friend_add[6], 'friends': Boulean, 'if_blocked': if_blocked[0], 'sender_id': sender_id, 'current_id': str(current_id[0])}
        return render_template('someone.html', **context3)

@app.route('/group')
def group():
        curs = conn.cursor()
        id = request.args.get('id')
        group_data = curs.execute("select * from users where id = '{}'".format(id)).fetchone()
        group_add_data = curs.execute("select * from users_add where user = '{}'".format(id)).fetchone()
        try:
            current_sesion = session['email']
            current_sesion = True
        except KeyError:
            current_sesion = False

        if current_sesion:
            current_email = session['email']
            current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
            print(current_id[0], group_data[7])
            if int(current_id[0]) == int(group_data[7]):
                status = 'owner'
                following = curs.execute("select * from groups where user_id = '{}' and group_id = '{}'".format(current_id[0], group_data[0])).fetchone()
            else:
                status = 'other'
                following = curs.execute("select * from groups where user_id = '{}' and group_id = '{}'".format(current_id[0], group_data[0])).fetchone()
        else:
            status = 'notLoggedIn'
            following = 'nope'

        user_model = user_info(curs, session['email'])
        context3 = {'user': user_model, 'group_data': group_data, 'group_add_data': group_add_data, 'status': status, 'following': following}
        return render_template('group_page.html', **context3)


@app.route('/group_action', methods=['POST'])
def group_action():
    action = request.json['action']
    group_id = request.json['id']
    curs = conn.cursor()
    user_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
    if action == "follow":
        validation = curs.execute("SELECT * FROM groups WHERE user_id = '{}' and group_id = '{}'".format(user_id, group_id)).fetchone()
        if validation:
            return redirect(url_for('return_home'))

        curs.execute("INSERT INTO groups ('user_id', 'group_id', 'block')  VALUES ('{}','{}','{}')".format(user_id, group_id, 0))
        conn.commit()

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully followed the group!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'followed group' })
    elif action == "unfollow":
        validation = curs.execute("SELECT * FROM groups WHERE user_id = '{}' and group_id = '{}'".format(user_id, group_id)).fetchone()
        if not validation:
            return redirect(url_for('return_home'))

        curs.execute("DELETE FROM groups WHERE user_id = '{}' and group_id = '{}'".format(user_id, group_id))

        conn.commit()

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully unfollowed the group!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'unfollowed group' })
    elif action == "delete":
        try:
            valid = int(curs.execute("SELECT id FROM users WHERE email = '{}'".format(session['email'])).fetchone()[0])
        except KeyError:
            return redirect(url_for('return_home'))

        valid2 = int(curs.execute("SELECT email FROM users WHERE id = '{}'".format(group_id)).fetchone()[0])

        print(valid, valid2)

        if valid == valid2:
            print(True)
            curs.execute("UPDATE users SET user_photo= '{}', type='dead' WHERE id = '{}'".format('dead.jpg, dead_back.png', group_id))
            conn.commit()
            return jsonify({ 'status': 'deleted group' })
        else:
            return redirect(url_for('return_home'))
    elif action == "renew":
        try:
            valid = int(curs.execute("SELECT id FROM users WHERE email = '{}'".format(session['email'])).fetchone()[0])
        except KeyError:
            return redirect(url_for('return_home'))

        valid2 = int(curs.execute("SELECT email FROM users WHERE id = '{}'".format(group_id)).fetchone()[0])

        print(valid, valid2)

        if valid == valid2:
            print(True)
            curs.execute("UPDATE users SET user_photo= '{}', type='<UserType instance>' WHERE id = '{}'".format('default-user-image.png, default-background.png', group_id))
            conn.commit()
            return jsonify({ 'status': 'renewed group' })
        else:
            return redirect(url_for('return_home'))




def FriendConnectionValidation(curs, friend_add, current_id):
    if current_id:
        FriendConnectionValidation = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend_add[6])).fetchone()

        FriendConnectionValidation2 = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(friend_add[6], current_id[0])).fetchone()

        if FriendConnectionValidation:
            status = curs.execute("select block from name where user1_id = '{}' and user2_id = '{}'".format(current_id[0], friend_add[6])).fetchone()[0]
            print(status)
            if status == 0 or status == 1:
                Boulean = True
            elif status == 'waiting':
                Boulean = 'waiting'
            else:
                Boulean = 'undefined'
        elif FriendConnectionValidation2:
            status = curs.execute("select block from name where user2_id = '{}' and user1_id = '{}'".format(current_id[0], friend_add[6])).fetchone()[0]
            if status == 0 or status == 1:
                Boulean = True
            elif status == 'waiting':
                Boulean = 'waiting'
            else:
                Boulean ='undefined'
        else:
            Boulean = False
        print(Boulean)
        return Boulean
    else:
        Boulean = 'NotLoggedIn'
        return Boulean

@app.route('/friends_list')
def friends_list():
    action = request.args.get('action')
    user = request.args.get('user')
    group = request.args.get('group')
    if user:
        curs = conn.cursor()
        current_email = session['email']
        user_model = user_info(curs, session['email'])

        user_information = curs.execute("SELECT first_name, last_name FROM users WHERE id  = '{0}'".format(user)).fetchall()

        curs = conn.cursor()

        friends_list = curs.execute("SELECT user1_id, user2_id FROM name WHERE user2_id  = '{0}' or user1_id  = '{0}'".format(user)).fetchall()

        friends_list_new = []
        for i in friends_list:

            if int(i[0]) != int(user):
                friends_list_new.append(i[0])
            elif int(i[1]) != int(user):
                friends_list_new.append(i[1])

        print(friends_list_new)


        friends_list = []
        for b in friends_list_new:

            friend_info = list(curs.execute("SELECT * FROM users WHERE id  = '{}'".format(b)).fetchone())
            fr_quantity = curs.execute("select count(*) from name where user1_id = '{0}' or user2_id = '{0}'".format(b)).fetchone()

            friend_info.append(fr_quantity[0])
            friends_list.append(friend_info)

        conn.commit()
        print(friends_list)
        context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': 'all', 'address': '', 'id': '', 'friends': friends_list, 'block': 'none', 'user_information': user_information}
        return render_template('friends.html', **context3)
    if group:
        curs = conn.cursor()
        current_email = session['email']
        user_model = user_info(curs, session['email'])
        print(group)
        user_information = curs.execute("SELECT first_name, last_name FROM users WHERE id  = '{0}'".format(group)).fetchall()

        curs = conn.cursor()

        friends_list = curs.execute("SELECT user_id FROM groups WHERE group_id  = '{0}'".format(group)).fetchall()

        friends_list_new = []
        for i in friends_list:

            if int(i[0]) != int(group):
                friends_list_new.append(i[0])
            elif int(i[1]) != int(group):
                friends_list_new.append(i[1])

        print(friends_list_new)


        friends_list = []
        for b in friends_list_new:

            friend_info = list(curs.execute("SELECT * FROM users WHERE id  = '{}'".format(b)).fetchone())
            fr_quantity = curs.execute("select count(*) from name where user1_id = '{0}' or user2_id = '{0}'".format(b)).fetchone()

            friend_info.append(fr_quantity[0])
            friends_list.append(friend_info)

        conn.commit()
        print(friends_list)
        context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': 'all', 'address': '', 'id': '', 'friends': friends_list, 'block': 'none', 'user_information': user_information}
        return render_template('friends.html', **context3)
    if session:
        if action == 'show_all':
            curs = conn.cursor()
            current_email = session['email']
            user_model = user_info(curs, session['email'])
            groups = list(curs.execute("select id from users where not password = 'group_type'").fetchall())
            output = []
            for id in groups:
                user_el = curs.execute("select * from users where id = '{}'".format(id[0])).fetchone()
                user_el = list(user_el)

                fr_quantity = curs.execute("select count(*) from name where user1_id = '{0}' or user2_id = '{0}'".format(id[0])).fetchone()

                user_el.append(fr_quantity[0])

                output.append(user_el)

            groups = output

            conn.commit()
            context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': 'all', 'address': '', 'id': '', 'friends': groups, 'block': 'none'}
            return render_template('friends.html', **context3)


        else:
            curs = conn.cursor()
            current_email = session['email']
            current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
            friends_1col = list(curs.execute("select user2_id from name where user1_id = '{}'".format(current_id[0])).fetchall())
            friends_2col = list(curs.execute("select user1_id from name where user2_id = '{}'".format(current_id[0])).fetchall())
            print(list(friends_1col))
            friends_id = friends_1col + friends_2col
            print(friends_id)
            friend = []
            for id in friends_id:

                user_el = curs.execute("select * from users where id = '{}'".format(id[0])).fetchone()
                user_el = list(user_el)

                fr_quantity = curs.execute("select count(*) from name where user1_id = '{0}' or user2_id = '{0}'".format(id[0])).fetchone()

                user_el.append(fr_quantity[0])
                friend.append(user_el)

            print(friend)


            user_model = user_info(curs, session['email'])
            context3 = {'user': user_model, 'name': '', 'email': 'friends_list', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': friend, 'block': 'none'}
            return render_template('friends.html', **context3)

@app.route('/groups_list')
def groups_list():
    action = request.args.get('action')
    user = request.args.get('user')
    if user:
        curs = conn.cursor()
        current_email = session['email']
        user_model = user_info(curs, session['email'])

        user_information = curs.execute("SELECT first_name, last_name FROM users WHERE id  = '{}'".format(user)).fetchall()

        curs = conn.cursor()

        groups_list = curs.execute("SELECT group_id FROM groups WHERE user_id  = '{}'".format(user)).fetchall()

        groups_list_new = groups_list


        groups_list = []
        for b in groups_list_new:

            group_info = list(curs.execute("SELECT * FROM users WHERE id  = '{}'".format(b[0])).fetchone())

            fr_quantity = curs.execute("select count(*) from groups where group_id = '{}'".format(group_info[0])).fetchone()

            group_info.append(fr_quantity[0])

            groups_list.append(group_info)

        conn.commit()
        print(groups_list_new, groups_list)
        context3 = {'user': user_model, 'name': '', 'email': 'groups_list', 'age': '', 'phone':  '', 'sex': 'all', 'address': '', 'id': '', 'friends': groups_list, 'block': 'none', 'user_information': user_information}
        return render_template('groups.html', **context3)
    if session:
        if action == 'show_all':
            curs = conn.cursor()
            current_email = session['email']
            user_model = user_info(curs, session['email'])
            groups = list(curs.execute("select id from users where password = 'group_type'").fetchall())
            output = []
            for id in groups:
                user_el = curs.execute("select * from users where id = '{}'".format(id[0])).fetchone()
                user_el = list(user_el)

                fr_quantity = curs.execute("select count(*) from groups where group_id = '{}'".format(id[0])).fetchone()

                user_el.append(fr_quantity[0])

                output.append(user_el)

            groups = output

            conn.commit()
            context3 = {'user': user_model, 'name': '', 'email': 'groups_list', 'age': '', 'phone':  '', 'sex': 'all', 'address': '', 'id': '', 'friends': groups, 'block': 'none'}
            return render_template('groups.html', **context3)
        else:
            curs = conn.cursor()
            current_email = session['email']
            user_model = user_info(curs, session['email'])
            current_id = curs.execute("select id from users where email = '{}'".format(current_email)).fetchone()
            groups = list(curs.execute("select group_id from groups where user_id = '{}'".format(current_id[0])).fetchall())
            output = []
            for id in groups:
                user_el = curs.execute("select * from users where id = '{}'".format(id[0])).fetchone()
                user_el = list(user_el)

                fr_quantity = curs.execute("select count(*) from groups where group_id = '{}'".format(id[0])).fetchone()

                user_el.append(fr_quantity[0])

                output.append(user_el)
            # print(groups)
            # output = []
            # for i in range(0, len(groups)):
            #     output.append(groups[i][0])
            #     print(output)
            groups = output

        context3 = {'user': user_model, 'name': '', 'email': 'groups_list', 'age': '', 'phone':  '', 'sex': '', 'address': '', 'id': '', 'friends': groups, 'block': 'none'}
        return render_template('groups.html', **context3)

@app.route('/add_friend', methods=['POST'])
def add_friendTEST():
    id = request.json['id']
    action=request.json['action']

    if action == "unfriend":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id
        print(user1_id, user2_id)
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()

        if f_col:
            curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = '{}' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id, user2_id)).fetchone()
            conn.commit()
        elif s_col:
            curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = '{}' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user2_id, user1_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully unfriended!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'unfriended' })
    elif action == "block":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            curs.execute("UPDATE name SET block = 1 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            curs.execute("UPDATE name SET block = 1 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            if user1_id:
                curs.execute("INSERT INTO name ('user1_id', 'user2_id', 'block', 'sender_id') VALUES('{}','{}','{}','{}')" \
                .format(user1_id, user2_id, 1, user1_id))
                conn.commit()
            else:
                return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully blocked ' + str(friend_name1[0] + ' ' + friend_name2[0]) + ' !', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'blocked' })
    elif action == "unblock":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            status = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()[0]
            print(status)
            if status == 'egal':
                curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            else:
                curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            status = curs.execute("select sender_id from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()[0]
            print('status:', status)
            if status == 'egal':
                curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            else:
                print('second')
                curs.execute("UPDATE name SET block = 'waiting' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully unblocked ' + str(friend_name1[0] + ' ' + friend_name2[0]) + ' !', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'unblocked' })
    elif action == "redo_request":
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()
        if not user1_id:
            return redirect(url_for('return_home'))
        user1_id = user1_id[0]
        user2_id = id
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        friend_name1 = curs.execute("select first_name from users where id = '{}'".format(user2_id)).fetchone()
        friend_name2 = curs.execute("select last_name from users where id = '{}'".format(user2_id)).fetchone()

        if s_col:
            curs.execute("DELETE FROM name WHERE user1_id = '{}' and  user2_id  = '{}'".format(user2_id, user1_id))
            conn.commit()
        elif f_col:
            curs.execute("DELETE FROM name WHERE user2_id = '{}' and  user1_id  = '{}'".format(user2_id, user1_id))
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        f_name = curs.execute("SELECT first_name from users WHERE id ='{}'" \
                .format(user1_id)).fetchone()
        l_name = curs.execute("SELECT last_name from users WHERE id ='{}'" \
                              .format(user1_id)).fetchone()
        user_from = 'friend request from ' + str(f_name[0]) + ' ' + str(l_name[0])

        notific_id = curs.execute("SELECT id from notifications WHERE text ='{}' and receiver_id = '{}'" \
                              .format(user_from, user2_id)).fetchone()[0]
        notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                              .format(user2_id)).fetchone()[0]
        notifications = notifications.split('{},'.format(notific_id))
        new_string = ''
        for i in notifications:
            if i:
                new_string = new_string + i

        notifications = new_string

        print(notifications)
        curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                     .format(notifications, user2_id))

        curs.execute("DELETE FROM notifications WHERE text = '{}' and  receiver_id  = '{}'" \
                 .format(user_from, user2_id))
        conn.commit()



        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Succesfully canceled friend request!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'request redo' })
    elif action == "accept":
        type = request.json['type']
        curs = conn.cursor()
        if type == "profile_accept":
            user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()
            if not user1_id:
                return redirect(url_for('return_home'))
            user1_id = user1_id[0]
            user2_id = id
        else:
            notific_id = request.args.get('notific_id')
            user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()
            print(user1_id, notific_id)
            if user1_id == None and notific_id == '0':
                user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
            elif user1_id != None and notific_id != '0':
                user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()[0]
            else:
                return redirect(url_for('return_home'))

            user2_id = id

            print(user1_id, user2_id)
        f_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        s_col = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        if s_col:
            curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = 'egal' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user2_id, user1_id)).fetchone()
            conn.commit()
        elif f_col:
            curs.execute("UPDATE name SET block = 0 WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            curs.execute("UPDATE name SET sender_id = 'egal' WHERE user1_id  = '{}' and user2_id  = '{}'".format(user1_id, user2_id)).fetchone()
            conn.commit()
        else:
            return redirect(url_for('return_home'))

        if type == "profile_accept":
            pass
            #curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()
        else:
            curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()

            notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                                  .format(user2_id)).fetchone()[0]
            notifications = notifications.split('{},'.format(notific_id))
            new_string = ''
            for i in notifications:
                if i:
                    new_string = new_string + i

            notifications = new_string

            curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                         .format(notifications, user2_id))

        conn.commit()
        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request accepted!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'accepted' })
    elif action == "decline":
        curs = conn.cursor()
        notific_id = request.args.get('notific_id')

        user1_id = curs.execute("SELECT sender_id from notifications WHERE id ='{}'".format(notific_id)).fetchone()
        if not user1_id:
            return redirect(url_for('return_home'))
        user1_id = user1_id[0]
        user2_id = id

        curs.execute("DELETE FROM notifications WHERE id  = '{}'".format(notific_id)).fetchone()

        notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                              .format(user2_id)).fetchone()[0]
        notifications = notifications.split('{},'.format(notific_id))
        new_string = ''
        for i in notifications:
            if i:
                new_string = new_string + i

        notifications = new_string

        curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                     .format(notifications, user2_id))

        conn.commit()
        user_model = user_info(curs, session['email'])
        notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
        notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
        if notifications_id[0] == None:
            notifications = []
            print('none')
        else:
            notifications_id = notifications_id[0].split(',')
        context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request declined!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
        return jsonify({ 'status': 'declined' })
    else: #become friends
        curs = conn.cursor()
        user1_id = curs.execute("SELECT id from users WHERE email ='{}'".format(session['email'])).fetchone()[0]
        user2_id = id

        FriendConnectionValidation = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user1_id, user2_id)).fetchone()
        FriendConnectionValidation2 = curs.execute("select * from name where user1_id = '{}' and user2_id = '{}'".format(user2_id, user1_id)).fetchone()
        if FriendConnectionValidation or FriendConnectionValidation2:
            return redirect(url_for('return_home'))
        else:
            curs.execute("INSERT INTO name ('user1_id', 'user2_id', 'block', 'sender_id') VALUES('{}','{}','{}','{}')" \
                .format(user1_id, user2_id, 'waiting', user1_id))
            f_name = curs.execute("SELECT first_name from users WHERE id ='{}'" \
                .format(user1_id)).fetchone()
            l_name = curs.execute("SELECT last_name from users WHERE id ='{}'" \
                                  .format(user1_id)).fetchone()
            user_from = 'friend request from ' + str(f_name[0]) + ' ' + str(l_name[0])
            print(user_from)
            curs.execute("INSERT INTO notifications ('text', 'receiver_id', 'sender_id') VALUES('{}', '{}', '{}')" \
                         .format(user_from, user2_id, user1_id))
            notific_id = curs.execute("SELECT id from notifications WHERE text ='{}' and receiver_id = '{}'" \
                                  .format(user_from, user2_id)).fetchone()[0]
            notifications = curs.execute("SELECT notifications from users WHERE id ='{}'" \
                                  .format(user2_id)).fetchone()[0]
            if notifications:
                notifications = str(notifications) + str(notific_id) + ','
            else:
                notifications = str(notific_id) + ','
            print(notifications)
            curs.execute("UPDATE users SET notifications = '{}' WHERE id  = '{}'" \
                         .format(notifications, user2_id))
            conn.commit()


            user_model = user_info(curs, session['email'])
            notifications = curs.execute("select text from notifications where receiver_id = '{}'".format(user_model.id)).fetchall()
            notifications_id = curs.execute("select notifications from users where id = '{}'".format(user_model.id)).fetchone()
            if notifications_id[0] == None:
                notifications = []
                print('none')
            else:
                notifications_id = notifications_id[0].split(',')
            context2 = {'block': 'block', 'd_none': 'none', 'user': user_model, 'messages': 'Friend request succesfully sent!', 'notifications': notifications, 'notifications_id': notifications_id, 'length': len(notifications)}
            return jsonify({ 'status': 'request sent' })

@app.route('/add_friend', methods=['GET'])
def add_friend():
    pass

#redirect(request.referrer)

@app.route('/upload', methods=['POST'])
def upload():
    type = request.args.get('type')
    user_type = request.args.get('user_type')
    curs = conn.cursor()
    if user_type == 'group':
        user_model = user_info(curs, 'group ' + request.args.get('id'))
    elif user_type == 'user':
        user_model = user_info(curs, session['email'])

    #if user_type == 'group':
        #target = os.path.join(APP_ROOT, 'static/images/' + str(user_model.id)) #path to user folder

    target = os.path.join(APP_ROOT, 'static/images/' + str(user_model.id)) #path to user folder
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target) #create user folder if it doesn`t exist

    print('dd', request.files.getlist(type))
    for file in request.files.getlist(type):
        save(user_model, curs, target, file, type)

    return jsonify({ 'status': 'Success' })


def save(user_model, curs, target, file, type):
    print(file)
    filenames = [f for f in listdir(target) if isfile(join(target, f))] #get all filenames
    try:
        filenames.remove('.DS_Store')
    except ValueError:
        pass
    print('list', filenames)


    number = 1
    for filename in filenames:
        number_current = int(filename.split('_')[1].split('.')[0]) #get all file numbers
        if number_current > number:
            number = number_current

    filename_origin = file.filename.split('.')[-1] #get file extension


    filename = type + '_' + str(number + 1) + '.' + str(filename_origin)

    destination = "/".join([target, filename]) #where to save
    user_photo = curs.execute("SELECT user_photo FROM users WHERE id  = '{}'".format(user_model.id)).fetchone()[0]
    print(user_photo)

    if type == 'ava':
        database_destination = destination.split(APP_ROOT + '/static/images/')[1] + ',' + user_photo.split(',')[1]
    elif type == 'back':
        database_destination =user_photo.split(',')[0] + ',' + destination.split(APP_ROOT + '/static/images/')[1]


    print(database_destination)

    curs.execute("UPDATE users SET user_photo = '{}' WHERE id  = '{}'".format(database_destination, user_model.id))
    conn.commit()

    try:
        file.save(destination)
    except:
        return jsonify({ 'status': 'Failed' })

@app.route('/images', methods=['GET'])
def images():
    curs = conn.cursor()

    user_model = user_info(curs, session['email'])

    target = os.path.join(APP_ROOT, 'static/images/' + str(user_model.id)) #path to user folder
    filenames = [f for f in listdir(target) if isfile(join(target, f))] #get all filenames
    try:
        filenames.remove('.DS_Store')
    except ValueError:
        pass
    print('list', filenames)


    output = []
    for filename in filenames:
        output.append(filename)

    print('list2', output)

    context2 = {'user': user_model,'origin_way': target.split('/')[-1] + '/', 'photos': output}
    return render_template('my_photos.html', **context2)

@app.route('/group_create', methods=['GET'])
def group_create():
    curs = conn.cursor()

    user_model = user_info(curs, session['email'])

    context2 = {'user': user_model}
    return render_template('group_create.html', **context2)


@app.route('/group_create', methods=['POST'])
def group_create_post():
    curs = conn.cursor()

    curs.execute('Delete from users where id=86')
    curs.execute('Delete from users where id=87')
    curs.execute('Delete from users where id=88')

    conn.commit()
    # group_name = request.json['name']
    # description = request.json['description']
    # location = request.json['location']

    user_model = user_info(curs, session['email'])

    context2 = {'user': user_model}
    return render_template('group_create.html', **context2)

@app.route('/delete_account', methods=['POST'])
def delete_account():

    try:
        current_sesion = session['email']
        current_sesion = True
    except KeyError:
        current_sesion = False

    if current_sesion:
        curs = conn.cursor()
        current_email = session['email']
        user_model = user_info(curs, session['email'])

        curs.execute("UPDATE users SET type = 'dead' WHERE id  = '{}'".format(user_model.id))

        conn.commit()

        del session['email']

        return jsonify({ 'status': 'deleted!' })


@app.route('/renew_account', methods=['POST'])
def renew_account():

    try:
        current_sesion = session['email']
        current_sesion = True
    except KeyError:
        current_sesion = False

    if current_sesion:
        curs = conn.cursor()
        current_email = session['email']
        user_model = user_info(curs, session['email'])

        curs.execute("UPDATE users SET type = 'live' WHERE id  = '{}'".format(user_model.id))

        conn.commit()


        return jsonify({ 'status': 'renewed!' })

@app.route('/get_friends', methods=['POST'])
def get_friends():
    id = request.json['id']
    action = request.json['action']
    start = request.json['start']
    end = request.json['end']
    try:
        quantity = request.json['give_me_quantity']
    except KeyError:
        quantity = None

    curs = conn.cursor()

    friends_list = curs.execute("SELECT user1_id, user2_id FROM name WHERE user2_id  = '{0}' or user1_id  = '{0}' ORDER BY id LIMIT '{1}', '{2}'".format(id, start, 8)).fetchall()

    friends_list_new = []
    for i in friends_list:

        if int(i[0]) != int(id):
            friends_list_new.append(i[0])
        elif int(i[1]) != int(id):
            friends_list_new.append(i[1])

    print(friends_list_new)

    if len(friends_list_new) < int(end) - int(start):
        end_of_friends = 'true'
    else:
        end_of_friends = 'false'

    friends_list = []
    for b in friends_list_new:

        friend_info = curs.execute("SELECT id, first_name, last_name, user_photo FROM users WHERE id  = '{}'".format(b)).fetchone()

        friends_list.append(friend_info)

    #count quantity if needed
    if quantity:
        fr_quantity = curs.execute("select count(*) from name where user1_id = '{0}' or user2_id = '{0}'".format(id)).fetchone()[0]
    else:
        fr_quantity = None

    print('blabla', id, action, start, end, friends_list, friends_list_new)

    return jsonify({ 'status': 'success!', 'end_of_friends': end_of_friends, 'friends_list': friends_list, 'quantity': fr_quantity })

@app.route('/get_groups', methods=['POST'])
def get_groups():
    id = request.json['id']
    action = request.json['action']
    start = request.json['start']
    end = request.json['end']
    try:
        quantity = request.json['give_me_quantity']
    except KeyError:
        quantity = None

    curs = conn.cursor()

    groups_list = curs.execute("SELECT group_id FROM groups WHERE user_id  = '{0}' ORDER BY id LIMIT '{1}', '{2}'".format(id, start, 8)).fetchall()

    groups_list_new = groups_list

    print(groups_list_new)

    if len(groups_list_new) < int(end) - int(start):
        end_of_friends = 'true'
    else:
        end_of_friends = 'false'

    groups_list = []
    for b in groups_list_new:

        friend_info = curs.execute("SELECT id, first_name, last_name, user_photo FROM users WHERE id  = '{}'".format(b[0])).fetchone()

        groups_list.append(friend_info)

    #count quantity if needed
    if quantity:
        gr_quantity = curs.execute("select count(*) from groups where user_id = '{0}'".format(id)).fetchone()[0]
    else:
        gr_quantity = None


    print('blabla', id, action, start, end, groups_list, groups_list_new)

    return jsonify({ 'status': 'success!', 'end_of_friends': end_of_friends, 'friends_list': groups_list, 'quantity': gr_quantity })

@app.route('/get_followers', methods=['POST'])
def get_followers():
    id = request.json['id']
    action = request.json['action']
    start = request.json['start']
    end = request.json['end']
    try:
        quantity = request.json['give_me_quantity']
    except KeyError:
        quantity = None

    curs = conn.cursor()

    friends_list = curs.execute("SELECT user_id FROM groups WHERE group_id  = '{0}' ORDER BY id LIMIT '{1}', '{2}'".format(id, start, 8)).fetchall()

    friends_list_new = []
    for i in friends_list:

        if int(i[0]) != int(id):
            friends_list_new.append(i[0])
        elif int(i[1]) != int(id):
            friends_list_new.append(i[1])

    print('ff', friends_list_new)

    if len(friends_list_new) < int(end) - int(start):
        end_of_friends = 'true'
    else:
        end_of_friends = 'false'

    friends_list = []
    for b in friends_list_new:

        friend_info = curs.execute("SELECT id, first_name, last_name, user_photo FROM users WHERE id  = '{}'".format(b)).fetchone()

        friends_list.append(friend_info)

    #count quantity if needed
    if quantity:
        fr_quantity = curs.execute("select count(*) from groups where group_id = '{0}'".format(id)).fetchone()[0]
    else:
        fr_quantity = None

    print('blabla', id, action, start, end, friends_list, friends_list_new)

    return jsonify({ 'status': 'success!', 'end_of_friends': end_of_friends, 'friends_list': friends_list, 'quantity': fr_quantity })


@app.route('/post', methods=['POST'])
def post():
    curs = conn.cursor()
    user_model = user_info(curs, session['email'])

    #if user_type == 'group':
        #target = os.path.join(APP_ROOT, 'static/images/' + str(user_model.id)) #path to user folder

    target = os.path.join(APP_ROOT, 'static/images/' + str(user_model.id)) #path to user folder
    print(target)

    if not os.path.isdir(target):
        os.mkdir(target) #create user folder if it doesn`t exist

    print(request.files, request.files.getlist('new_post_images'))

    try:
        post = UserManager().getPostData(request.form, user_model.id)
    except schematics.exceptions.DataError:
        context = {'errors': 'Wrong Data'}
        return jsonify({ 'status': 'Error' })


    post_id = post.addNewPost()

    print(post_id)



    count = 0
    for file in request.files.getlist('new_post_images'):
        count += 1
        if count < 5:
            print(file)
            save2(user_model, curs, target, file, post_id, count)




    return jsonify({ 'status': 'Success', 'post_id': post_id})


def save2(user_model, curs, target, file, id, count):
    print(file)

    filename_origin = file.filename.split('.')[-1] #get file extension


    filename = 'post_' + str(id) + '_' + str(count + 1) + '.' + str(filename_origin)

    destination = "/".join([target, filename]) #where to save

    post_photo = curs.execute("SELECT images FROM posts WHERE id  = '{}'".format(id)).fetchone()[0]
    print('post_photo:', post_photo, destination)

    if post_photo != '':
        print('if')
        database_destination = post_photo + destination.split(APP_ROOT + '/static/images/')[1] + ','
    else:
        print('else')
        database_destination = destination.split(APP_ROOT + '/static/images/')[1] + ','

    print(database_destination)

    curs.execute("UPDATE posts SET 'images' = '{}' WHERE id  = '{}'".format(database_destination, id))
    conn.commit()

    try:
        file.save(destination)
    except:
        return jsonify({ 'status': 'Failed' })

@app.route('/get_posts', methods=['POST'])
def get_posts():
    id = request.json['id']
    action = request.json['action']
    start = request.json['start']
    end = request.json['end']

    curs = conn.cursor()

    posts_list = curs.execute("SELECT id FROM posts WHERE user_id  = '{0}' ORDER BY id DESC LIMIT '{1}', '{2}'".format(id, start, 5)).fetchall()

    posts_list_new = posts_list

    print(posts_list_new)

    if len(posts_list_new) < int(end) - int(start):
        end_of_posts = 'true'
    else:
        end_of_posts = 'false'

    posts_list = []
    for b in posts_list_new:

        post_info = list(curs.execute("SELECT id, user_id, text, images, tags, location, date, status FROM posts WHERE id  = '{}'".format(b[0])).fetchone())
        post_reactions_quantity = curs.execute("select count(*) from reactions where post_id = '{0}'".format(b[0])).fetchone()[0]
        post_comm_quantity = curs.execute("select count(*) from comments where post_id = '{0}'".format(b[0])).fetchone()[0]
        post_reactions = curs.execute("SELECT user_id, reaction FROM reactions WHERE post_id  = '{}'".format(b[0])).fetchall()
        post_user = curs.execute("SELECT * FROM users WHERE id  = '{}'".format(post_info[1])).fetchone()

        post_info.append(post_reactions_quantity)
        post_info.append(post_reactions)
        post_info.append(post_user)
        post_info.append(post_comm_quantity)
        print('post_info', post_info)
        posts_list.append(post_info)



    print('blabla', id, action, start, end, posts_list, posts_list_new)

    return jsonify({ 'status': 'success!', 'end_of_posts': end_of_posts, 'posts_list': posts_list })

@app.route('/reaction', methods=['POST'])
def reaction():
    curs = conn.cursor()
    user_model = user_info(curs, session['email'])

    reaction = request.json['reaction']
    post_id = request.json['post_id']
    date = request.json['date']

    curs.execute("DELETE FROM reactions WHERE user_id = '{}' and post_id = '{}'".format(user_model.id, post_id))
    conn.commit()
    curs.execute("INSERT INTO reactions ('user_id', 'post_id', 'reaction', 'date')  VALUES ('{}','{}','{}','{}')" \
            .format(user_model.id, post_id, reaction, date))
    conn.commit()

    return jsonify({ 'status': 'success!' })

@app.route('/remove_reaction', methods=['POST'])
def remove_reaction():
    curs = conn.cursor()
    user_model = user_info(curs, session['email'])

    post_id = request.json['post_id']

    curs.execute("DELETE FROM reactions WHERE user_id = '{}' and post_id = '{}'".format(user_model.id, post_id))

    conn.commit()

    return jsonify({ 'status': 'success!' })

@app.route('/add_comment', methods=['POST'])
def add_comment():
    curs = conn.cursor()
    user_model = user_info(curs, session['email'])

    text = request.json['text']
    post_id = request.json['post_id']
    date = request.json['date']


    curs.execute("INSERT INTO comments ('user_id', 'post_id', 'text', 'date')  VALUES ('{}','{}','{}','{}')" \
            .format(user_model.id, post_id, text, date))

    conn.commit()

    id = curs.execute("SELECT id FROM comments WHERE user_id  = '{}' and post_id  = '{}' and text  = '{}' and date  = '{}'".format(user_model.id, post_id, text, date)).fetchall()
    print(id[0][0])
    curs.execute("UPDATE comments SET comm_id = '{}' WHERE id = '{}'".format('comm_'+str(id[0][0]), id[0][0]))

    conn.commit()

    return jsonify({ 'status': 'success!' , 'comm_id': 'comm_'+str(id[0][0])})

@app.route('/get_comments', methods=['POST'])
def get_comments():
    curs = conn.cursor()
    user_model = user_info(curs, session['email'])

    post_id = request.json['post_id']
    start = request.json['start']
    end = request.json['end']

    comments_list = list(curs.execute("SELECT * FROM comments WHERE post_id  = '{}' ORDER BY id DESC LIMIT '{}', '{}'".format(post_id, start, int(end)-int(start))).fetchall())
    comments_quantity = curs.execute("select count(*) from comments where post_id = '{}'".format(post_id)).fetchone()[0]

    comments_list_new = []
    for b in comments_list:
        b=list(b)
        comment_user = list(curs.execute("SELECT * FROM users WHERE id  = '{}'".format(b[2])).fetchone())
        print(b,comment_user)
        b.append(comment_user)
        comments_list_new.append(b)

    print(len(comments_list_new), int(end), int(start))

    if len(comments_list_new) < int(end) - int(start):
        end_of_comm = 'true'
    else:
        end_of_comm = 'false'

    if int(start) == 0:
        if comments_quantity > 1:
            end_of_comm = 'false'
        else:
            end_of_comm = 'true'


    print(comments_list_new, comments_quantity, end_of_comm)

    return jsonify({ 'status': 'success!', 'comments_list': comments_list_new, 'comments_quantity': comments_quantity, 'end_of_comm': end_of_comm })

@app.route('/get_reactions', methods=['POST'])
def get_reactions():
    print(request.json)
    post_id = request.json['post_id']
    start = request.json['start']
    end = request.json['end']

    curs = conn.cursor()

    react_list = curs.execute("SELECT user_id, reaction FROM reactions WHERE post_id  = '{0}' ORDER BY id DESC LIMIT '{1}', '{2}'".format(post_id, start, 10)).fetchall()

    react_list_new = react_list

    print(react_list)

    if len(react_list_new) < int(end) - int(start):
        end_of_reacts = 'true'
    else:
        end_of_reacts = 'false'

    react_list = []
    for b in react_list_new:
        b = list(b)
        react_user = curs.execute("SELECT * FROM users WHERE id  = '{}'".format(b[0])).fetchone()
        b.append(react_user)

        react_list.append(b)



    print('blabla', id, start, end, react_list, react_list_new)

    return jsonify({ 'status': 'success!', 'end_of_reacts': end_of_reacts, 'react_list': react_list })




if __name__ =='__main__':
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True
    app.run(port=5004)



