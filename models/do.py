
import sqlite3

conn = sqlite3.connect('database.sqlite3')
curs = conn.cursor()

curs.execute('''
CREATE TABLE users_add (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
age integer ,
create_time TEXT  NOT NULL,
phone TEXT,
address TEXT,
sex integer,
user integer NOT NULL,
FOREIGN KEY(user) REFERENCES users(id)
)
''')

conn.commit()

curs.execute('''
CREATE TABLE user_type (
id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
type_name TEXT NOT NULL,
create_time TEXT  NOT NULL
)
''')

conn.commit()

# curs.execute('drop table users')
# conn.commit()

curs.execute('''
  CREATE TABLE users (
  id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  first_name  TEXT NOT NULL,
  last_name  TEXT,
  type INTEGER NOT NULL,
  descr TEXT,
  user_photo TEXT,
  user_photos TEXT,
  email  TEXT NOT NULL,
  password TEXT NOT NULL,
  create_time TEXT  NOT NULL,
  FOREIGN KEY(type) REFERENCES user_type(id)
  ) ''')

conn.commit()

conn.close()
