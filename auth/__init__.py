import hashlib
import os
import typing

from fastapi import HTTPException, Depends
from fastapi.security import OAuth2AuthorizationCodeBearer

from database import get_db
from models import LoginData, LoginResponse


def hash_pass(passwd: str) -> bytes:
    return hashlib.blake2b(bytes(passwd)).digest()


def create_token() -> str:
    b = os.urandom(24)
    return b.hex()


__tokens = {"foo"}


def login(body: LoginData) -> LoginResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT Id, Passwd FROM Auth WHERE Name = ?", (body.uname,))
        data = cur.fetchone()
        if data is not None and len(data):
            # stuff got fetched
            if hash_pass(body.passwd) == data[2]:
                # auth success
                token = create_token()
                __tokens.add(token)
                return LoginResponse(token=token)
            else:
                raise HTTPException(status_code=401, detail="INVALID_PASSWD")
        else:
            raise HTTPException(status_code=401, detail="INVALID_PASSWD")
    except Exception as e:
        raise e


def validate_login(header: str) -> bool:
    print(header)
    # format is Bearer <token>
    if header is None:
        return False
    token = header.split("Bearer ")[-1]
    return token in __tokens


def secure_endpoint(typevar: typing.Type):
    def internal(fun):
        return _secure_endpoint(fun, typevar)

    return internal


oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="/login", authorizationUrl="/login")


def _secure_endpoint(fun, typevar: typing.Type):
    def inner(data: typevar, token: str | None = Depends(oauth2_scheme)):
        if validate_login(token):
            return fun(data)
        else:
            raise HTTPException(status_code=401, detail="UNAUTHORIZED")

    return inner
