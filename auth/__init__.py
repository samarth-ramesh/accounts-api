import hashlib
import os
import sqlite3
import typing

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer

from database import get_db
from models import LoginResponse


def hash_pass(passwd: str) -> bytes:
    return hashlib.blake2b(bytes(passwd, encoding="utf-8")).digest()


def create_token() -> str:
    b = os.urandom(24)
    return b.hex()


__tokens = {"foo"}


def login(body: OAuth2PasswordRequestForm) -> LoginResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT Id, Passwd FROM Auth WHERE Name = ?", (body.username,))
        data = cur.fetchone()
        if data is not None and len(data):
            # stuff got fetched
            if hash_pass(body.password) == data[1]:
                # auth success
                token = "foo" # create_token()
                __tokens.add(token)
                return LoginResponse(access_token=token)
            else:
                raise HTTPException(status_code=401, detail="INVALID_PASSWD")
        else:
            raise HTTPException(status_code=401, detail="INVALID_PASSWD")
    except Exception as e:
        raise e


def validate_login(header: str) -> bool:
    # format is Bearer <token>
    if header is None:
        return False
    token = header.split("Bearer ")[-1]
    return token in __tokens


def secure_endpoint(typevar: typing.Type):
    def internal(fun):
        return _secure_endpoint(fun, typevar)

    return internal


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def _secure_endpoint(fun, typevar: typing.Type):
    def inner(data: typevar, token: str | None = Depends(oauth2_scheme)):
        if validate_login(token):
            return fun(data)
        else:
            raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    return inner


def add_test_user():
    try:
        conn = get_db()
        cur = conn.execute("INSERT INTO Auth(Name, Passwd) VALUES (?,?)", ("srini", hash_pass("foo")))
        print(cur.rowcount)
        conn.commit()
    except sqlite3.Error:
        raise RuntimeError("Unable to add to db")


if __name__ == "__main__":
    add_test_user()
