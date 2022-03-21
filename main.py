from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

import accounts
import auth
import transactions
from models import LoginResponse, TransactionData, TransactionResponse, AccountData, Error, \
    AccountCreateResponse, AccountList, AccountListResponse

app = FastAPI()

responses = {401: {"model": Error}, 404: {"model": Error}}


@app.post(path="/login", response_model=LoginResponse, responses=responses)
def login(body: OAuth2PasswordRequestForm = Depends()):
    return auth.login(body)


@app.post(path="/transaction", response_model=TransactionResponse, responses=responses)
@auth.secure_endpoint(TransactionData)
def transaction(transaction_data: TransactionData):
    return transactions.create_transaction(transaction_data)


@app.post(path="/accounts/create", response_model=AccountCreateResponse, responses=responses)
@auth.secure_endpoint(AccountData)
def create_account(account_data: AccountData):
    return accounts.create_account(account_data)


@app.post(path="/accounts/list", response_model=AccountListResponse, responses=responses)
@auth.secure_endpoint(AccountList)
def get_accounts(account_data: AccountList):
    return accounts.get_accounts(account_data)
