import typing

from pydantic import BaseModel


class LoginResponse(BaseModel):
    access_token: str | None
    token_type: str = "Bearer"


class TransactionData(BaseModel):
    Amount: float
    Remarks: str
    A1: int
    A2: int


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


class TransactionList(BaseModel):
    Remarks: str | None
    StartTime: int | None
    EndTime: int | None
    MinAmount: float | None
    MaxAmount: float | None
    Account1: int | None
    Account2: int | None


class TransactionListItem(BaseModel):
    Amount: float
    Remarks: str
    Account1: str
    Account2: str
    TransactionTime: int
    Id: int


class TransactionListResponse(BaseModel):
    Transactions: typing.List[TransactionListItem]
