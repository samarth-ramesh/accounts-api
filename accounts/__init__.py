import sqlite3

from fastapi import HTTPException

from database import get_db
from models import AccountData, AccountCreateResponse, AccountList, AccountListResponse, AccountListItem


def is_def(name: str):
    return globals().get(name, None) is not None


def create_account(account_data: AccountData) -> AccountCreateResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO Account (Name) VALUES (?)", (account_data.Name,))
        cur.execute("SELECT Id, Amount, Name FROM Account WHERE Name = ?", (account_data.Name,))
        data = cur.fetchone()
        conn.commit()
        return AccountCreateResponse(Id=data["Id"], Amount=data["Amount"], Name=data["Name"])
    except sqlite3.Error:
        if is_def("conn"):
            conn.rollback()
        raise HTTPException(status_code=500, detail="DB_ERROR")
    except Exception as e:
        if is_def("conn"):
            conn.rollback()
        raise e
    finally:
        if is_def("conn"):
            conn.close()


def get_accounts(account_data: AccountList) -> AccountListResponse:
    def process_accounts(accounts: list[sqlite3.Row]):
        return AccountListResponse(
            Accounts=[AccountListItem(Id=i["Id"], Name=i["Name"], Amount=i["Amount"]) for i in accounts])

    try:
        conn = get_db()
        if account_data.Id is not None:
            # get account with id x
            cur = conn.execute("SELECT Id, Name, Amount FROM Account WHERE Id = ?", (account_data.Id,))
            data = cur.fetchone()
            if data:
                return AccountListResponse(
                    Accounts=[AccountListItem(Id=data["Id"], Name=data["Name"], Amount=data["Amount"])])
            else:
                raise HTTPException(status_code=404, detail="NO_ACCOUNT")
        elif account_data.Name is not None:
            wildcard_query = "%" + account_data.Name + "%"
            cur = conn.execute("SELECT Id, Name, Amount FROM Account WHERE Name LIKE ?", (wildcard_query,))

            data = cur.fetchall()
            return process_accounts(data)
        else:
            cur = conn.execute("SELECT Id, Name, Amount FROM Account")
            data = cur.fetchall()
            return process_accounts(data)

    except sqlite3.Error:
        raise HTTPException(status_code=500, detail="DB_ERROR")

    finally:
        if is_def("conn"):
            conn.close()
