import hashlib
import sqlite3

schema = """
CREATE TABLE Account(
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL ,
    Name TEXT UNIQUE NOT NULL,
    Amount NUMERIC NOT NULL DEFAULT 0);
CREATE TABLE Transactions(
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Amount NUMERIC NOT NULL,
    Remarks TEXT NOT NULL ,
    TransactionTime INTEGER NOT NULL,
    A1 INTEGER NOT NULL ,
    A2 INTEGER NOT NULL,
    FOREIGN KEY(A1) REFERENCES Account(Id),
    FOREIGN KEY(A2) REFERENCES Account(Id)
);
CREATE TABLE Auth(
    Id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    Name TEXT NOT NULL UNIQUE,
    Passwd BLOB NOT NULL
);
"""


def init_db():
    db = get_db()
    cur = db.cursor()
    cur.execute("SELECT name from sqlite_master WHERE type='table' AND name = 'Auth'")
    data = cur.fetchall()
    if len(data) == 0:
        cur.executescript(schema)
        cur.execute("INSERT INTO Auth (Name, Passwd) VALUES ('srini',?)", (hashlib.blake2b(b"foo").digest(),))
        db.commit()


__db_name = "./db/db.db"


def get_db():
    db = sqlite3.connect(__db_name)
    db.row_factory = sqlite3.Row
    return db


init_db()
