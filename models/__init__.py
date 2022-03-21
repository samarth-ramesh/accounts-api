import typing

from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str | None
    token_type: str = "Bearer"


class TransactionData(BaseModel):
    Amount: float
    Remarks: str
    A1: str
    A2: str


class TransactionResponse(BaseModel):
    Id: typing.Optional[int]
    Bal1: typing.Optional[float]
    Bal2: typing.Optional[float]


class AccountData(BaseModel):
    Name: str


class AccountCreateResponse(BaseModel):
    Id: typing.Optional[int]
    Name: typing.Optional[str]
    Amount: typing.Optional[float]


class Error(BaseModel):
    detail: str


class AccountList(BaseModel):
    Name: str | None
    Id: int | None


class AccountListItem(AccountList):
    Amount: float


class AccountListResponse(BaseModel):
    Accounts: typing.List[AccountListItem]
