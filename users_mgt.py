import os

from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table
from sqlalchemy.sql import select
from werkzeug.security import generate_password_hash

from config import engine

load_dotenv()

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))


class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    habit = db.Column(db.String(20))
    count = db.Column(db.Integer)


User_tbl = Table("user", User.metadata)
Habit_tbl = Table("habit", Habit.metadata)


def create_tables():
    User.metadata.create_all(engine)
    Habit.metadata.create_all(engine)


def add_user(username, password, email):
    hashed_password = generate_password_hash(password, method="sha256")

    ins = User_tbl.insert().values(
        username=username, email=email, password=hashed_password
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()


def add_habit(username, habit):
    insert = Habit_tbl.insert().values(username=username, habit=habit, count=0)

    conn = engine.connect()
    conn.execute(insert)
    conn.close()


def del_user(username):
    delete = User_tbl.delete().where(User_tbl.c.username == username)

    conn = engine.connect()
    conn.execute(delete)
    conn.close()


def show_users():
    select_st = select([User_tbl.c.username, User_tbl.c.email])

    conn = engine.connect()
    rs = conn.execute(select_st)

    for row in rs:
        print(row)

    conn.close()


def show_habits(username):
    stmt = select([Habit_tbl.c.username, Habit_tbl.c.habit]).where(
        Habit_tbl.c.username == username
    )

    conn = engine.connect()
    rs = conn.execute(stmt)

    res = []
    for row in rs:
        res.append(row)

    conn.close()
    return res

if __name__ == "__main__":
    #create_tables()
    #print('a')
    add_user('pep','admin','admin@test.com')