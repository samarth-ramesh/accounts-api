import datetime
import sqlite3

from fastapi import HTTPException

from database import get_db
from models import TransactionData, TransactionResponse, TransactionList, TransactionListItem, TransactionListResponse


def create_transaction(transdata: TransactionData) -> TransactionResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        current_time = datetime.datetime.utcnow().timestamp()
        cur.execute(
            "INSERT INTO Transactions (Amount, Remarks, A1, A2, TransactionTime) VALUES (? ,? ,?, ?, ?)",
            (transdata.Amount, transdata.Remarks, transdata.A1, transdata.A2, current_time))
        cur.execute("SELECT Id FROM Transactions ORDER BY Id DESC LIMIT 1")
        row_id = cur.fetchone()[0]
        cur.executemany("UPDATE Account SET Amount=Amount+? WHERE Id=?",
                        [(-transdata.Amount, transdata.A1), (transdata.Amount, transdata.A2)])
        cur.execute("SELECT Id, Amount FROM Account WHERE Id = ? OR Id = ?", (transdata.A1, transdata.A2,))
        data = cur.fetchall()
        if len(data) != 2:
            raise HTTPException(status_code=400, detail="NO_ACCOUNT")
        else:
            amounts = {data[0]["Id"]: data[0]["Amount"], data[1]["Id"]: data[1]["Amount"]}
        conn.commit()
        return TransactionResponse(Id=row_id, Bal1=amounts[transdata.A1], Bal2=amounts[transdata.A2])
    except sqlite3.Error as e:
        print(e)
        raise HTTPException(status_code=500, detail="DB_ERROR")
    except Exception as e:
        raise e


def get_transactions(params: TransactionList) -> TransactionListResponse:
    query = """SELECT T.Id, T.Amount, T.Remarks, T.TransactionTime,
        A1.Name AS AcFrom, A2.Name AS AcTo
        FROM Transactions as T
            JOIN Account A1 on A1.Id = T.A1
            JOIN Account A2 on A2.Id = T.A2  """
    query_params = []

    def start_guard():
        nonlocal query
        if not len(query_params):
            query += "WHERE "
        else:
            query += " AND "

    if params.Remarks:
        if not len(query_params):
            query += "WHERE "
        query += "Remarks LIKE ?"
        query_params.append("%" + params.Remarks + "%")

    if params.StartTime:
        start_guard()

        query += "TransactionTime > ?"
        query_params.append(params.StartTime)

    if params.EndTime:
        start_guard()

        query += "TransactionTime < ?"
        query_params.append(params.StartTime)

    if params.MinAmount:
        start_guard()
        query += "Amount > ?"
        query_params.append(params.MinAmount)

    if params.MaxAmount:
        start_guard()
        query += "Amount < ?"
        query_params.append(params.MaxAmount)

    if params.Account1:
        start_guard()
        query += "(A1 = ?) or (A2 = ?)"
        query_params += [params.Account1, params.Account1]

    if params.Account2:
        start_guard()
        query += "(A1 = ?) or (A2 = ?)"
        query_params += [params.Account2, params.Account2]

    try:
        con = get_db()
        cur = con.execute(query, tuple(query_params))
        data = cur.fetchall()
        rv = []
        for row in data:
            rv.append(TransactionListItem(
                Amount=row["Amount"],
                Remarks=row["Remarks"],
                Account1=row["AcFrom"],
                Account2=row["AcTo"],
                TransactionTime=row["TransactionTime"],
                Id=row["Id"]
            ))
        return TransactionListResponse(Transactions=rv)
    except Exception as e:
        raise e
