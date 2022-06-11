from urllib import response
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm

import accounts
import auth
import transactions
from models import LoginResponse, TransactionData, TransactionDelete, TransactionDeleteResponse, TransactionResponse, AccountData, Error, \
    AccountCreateResponse, AccountList, AccountListResponse, TransactionList, TransactionListResponse

app = FastAPI(
    servers=[
        {'url': 'https://ac.samarth.gq', 'description': 'Prod'},
        {'url': 'http://127.0.0.1:8000', 'description': 'Dev'}
    ]
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

responses = {401: {"model": Error}, 404: {"model": Error}}


@app.post(path="/login", response_model=LoginResponse, responses=responses)
def login(body: OAuth2PasswordRequestForm = Depends()):
    print(body)
    return auth.login(body)


@app.post(path="/transactions/create", response_model=TransactionResponse, responses=responses)
@auth.secure_endpoint(TransactionData)
def transaction(transaction_data: TransactionData):
    return transactions.create_transaction(transaction_data)


@app.post(path="/transactions/list", response_model=TransactionListResponse, responses=responses)
@auth.secure_endpoint(TransactionList)
def search_transaction(params: TransactionList) -> TransactionListResponse:
    return transactions.get_transactions(params)


@app.post(path="/accounts/create", response_model=AccountCreateResponse, responses=responses)
@auth.secure_endpoint(AccountData)
def create_account(account_data: AccountData):
    return accounts.create_account(account_data)


@app.post(path="/accounts/list", response_model=AccountListResponse, responses=responses)
@auth.secure_endpoint(AccountList)
def get_accounts(account_data: AccountList):
    return accounts.get_accounts(account_data)

@app.post(path="/transactions/delete", responses=responses, response_model=TransactionDeleteResponse)
@auth.secure_endpoint(TransactionDelete)
def delete_account(details: TransactionDelete):
    transdetails = transactions.delete_transaction(details.Id)
    return TransactionDeleteResponse(Status=transdetails);
