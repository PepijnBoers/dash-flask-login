import os

from sqlalchemy.sql import func
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Table, and_
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
    username = db.Column(db.String(15))
    habit = db.Column(db.String(20), default="Undefined")
    description = db.Column(db.String(180), default="No description")
    count = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime(timezone=True), server_default=func.now())
    updated = db.Column(db.DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    db.UniqueConstraint('username', 'habit', name='uix_1')
    


User_tbl = Table("user", User.metadata)
Habit_tbl = Table("habit", Habit.metadata)


def create_user_table():
    User.metadata.create_all(engine)

def drop_user_table():
    User.__table__.drop(engine)

def create_habit_table():
    Habit.metadata.create_all(engine)

def drop_habit_table():
    Habit.__table__.drop(engine)    


def add_user(username, password, email):
    hashed_password = generate_password_hash(password, method="sha256")

    ins = User_tbl.insert().values(
        username=username, email=email, password=hashed_password
    )

    conn = engine.connect()
    conn.execute(ins)
    conn.close()


def add_habit(username, habit, description, count):
    conn = engine.connect()
    select_st = select([Habit_tbl.c.habit]).where(Habit_tbl.c.username == username)
    if habit in [name[0] for name in conn.execute(select_st)]:
        conn.close()
    else:
        if not count:
            count = 0
        insert = Habit_tbl.insert().values(username=username, habit=habit, description=description, count=count)
        conn.execute(insert)
        conn.close()


def del_user(username):
    delete = User_tbl.delete().where(User_tbl.c.username == username)
    conn = engine.connect()
    conn.execute(delete)
    conn.close()

def del_habit(username, habit):
    delete = Habit_tbl.delete().where(and_(Habit_tbl.c.username == username, Habit_tbl.c.habit == habit))
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
    stmt = select([Habit_tbl.c.habit, Habit_tbl.c.description, Habit_tbl.c.count, Habit_tbl.c.updated, Habit_tbl.c.created]).where(
        Habit_tbl.c.username == username
    )

    conn = engine.connect()
    rs = conn.execute(stmt)

    res = []
    for row in rs:
        res.append(row)

    conn.close()
    return res


def update_habit_count(username: str, habit: str):
    conn = engine.connect()
    stmt = Habit_tbl.update().\
        values(count=Habit_tbl.c.count + 1).\
        where(Habit_tbl.c.username == username and Habit_tbl.c.habit == habit)
    conn.execute(stmt)
    conn.close()
    return db.session.query(Habit_tbl.c.count).filter(Habit_tbl.c.username.like(username),
    Habit_tbl.c.habit.like(habit)).first()


def reset_habit(username: str, habit:str):
    conn = engine.connect()
    stmt = Habit_tbl.update().\
        values(count=0).\
        where(Habit_tbl.c.username == username and Habit_tbl.c.habit == habit)
    conn.execute(stmt)
    conn.close()
    return 0


if __name__ == "__main__":
    #create_tables()
    #print('a')
    #add_user('pep','admin','ppep@test.com')
    drop_habit_table()
    create_habit_table()
    #add_habit('pep', 'Meditating 33', 'Meditate for 33 minutes')