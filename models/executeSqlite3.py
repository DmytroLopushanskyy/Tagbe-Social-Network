# -*- coding:utf-8 -*-

from sqlite3 import IntegrityError
from models import conn
import sqlite3
conn = sqlite3.connect('database.sqlite3', check_same_thread=False)

def executeSelectOne(sql):

    curs = conn.cursor()
    curs.execute(sql)
    data = curs.fetchone()

    return data

def executeSelectAll(sql):

    curs = conn.cursor()
    curs.execute(sql)
    data = curs.fetchall()

    return data

def executeSQL(sql):
    try:
        curs = conn.cursor()
        curs.execute(sql)
        conn.commit()
        return True
    except IntegrityError:
        return False

