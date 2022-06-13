import datetime
import sqlite3
from tkinter.messagebox import NO

from fastapi import HTTPException

from database import get_db
from models import TransactionData, TransactionEditData, TransactionResponse, TransactionList, TransactionListItem, TransactionListResponse


def create_transaction(transdata: TransactionData) -> TransactionResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        current_time = datetime.datetime.utcnow().timestamp()
        cur.execute(
            "INSERT INTO Transactions (Amount, Remarks, A1, A2, TransactionTime, IsDeleted) VALUES (? ,? ,?, ?, ?, FALSE)",
            (transdata.Amount, transdata.Remarks, transdata.A1, transdata.A2, current_time))
        cur.execute("SELECT Id FROM Transactions ORDER BY Id DESC LIMIT 1")
        row_id = cur.fetchone()[0]
        cur.executemany("UPDATE Account SET Amount=Amount+? WHERE Id=?",
                        [(-transdata.Amount, transdata.A1), (transdata.Amount, transdata.A2)])
        cur.execute("SELECT Id, Amount FROM Account WHERE Id = ? OR Id = ?",
                    (transdata.A1, transdata.A2,))
        data = cur.fetchall()
        if len(data) != 2:
            raise HTTPException(status_code=400, detail="NO_ACCOUNT")
        else:
            amounts = {data[0]["Id"]: data[0]["Amount"],
                       data[1]["Id"]: data[1]["Amount"]}
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
            JOIN Account A2 on A2.Id = T.A2 
        WHERE T.IsDeleted != TRUE """
    query_params = []

    def start_guard():
        query += " AND "

    if params.Remarks:
        query += "AND Remarks LIKE ?"
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
        return HTTPException(status_code=500, )


def undo_transaction(amount: int, acc1: int, acc2: int, cur: sqlite3.Cursor):
    "Undo the effect of a transaction"
    cur.execute(
        "UPDATE Account SET Amount = Amount + ? WHERE Id = ?", (amount, acc1))
    cur.execute(
        "UPDATE Account SET Amount = Amount - ? WHERE Id = ?", (amount, acc2))


def delete_transaction(transaction_id: int) -> bool:
    conn: sqlite3.Connection = get_db()
    cur: sqlite3.Cursor = conn.cursor()
    try:
        cur.execute(
            "SELECT Amount, A1, A2 FROM Transactions WHERE Id = ?", (transaction_id,))
        data = cur.fetchone()
        amount = data[0]
        acc1 = data[1]
        acc2 = data[2]
        undo_transaction(amount, acc1, acc2, cur)
        cur.execute(
            "UPDATE Transactions SET IsDeleted = TRUE WHERE Id = ?", (transaction_id,))
        conn.commit()
        return True
    except sqlite3.Error as ex:
        raise HTTPException(status_code=500, detail="DB_ERROR") from ex
    except Exception as exception:
        raise exception


def validate_account(cur: sqlite3.Cursor, acc: int) -> bool:
    cur.execute("SELECT Id FROM Account WHERE Id = ?", (acc, ))
    data = cur.fetchone()
    print(data)
    return data is None


def edit_transaction(transaction_data: TransactionEditData) -> TransactionListItem:
    "Edit transaction"
    conn: sqlite3.Connection = get_db()
    cur: sqlite3.Cursor = conn.cursor()

    cur.execute("SELECT Amount, A1, A2, Remarks FROM Transactions WHERE Id = ?",
                (transaction_data.Id,))

    data = cur.fetchone()

    if (data == None):
        raise HTTPException(status_code=404, detail="INVALID_ID")

    o_amount: float = data[0]
    o_acc1: int = data[1]
    o_acc2: int = data[2]
    o_remarks: str = data[3]

    print(o_acc1, transaction_data.A1)

    undo_transaction(o_amount, o_acc1, o_acc2, cur)

    if (transaction_data.Amount is not None and transaction_data.Amount != o_amount):
        n_amount = transaction_data.Amount
    else:
        n_amount = o_amount

    if (transaction_data.A1 is not None and transaction_data.A1 != o_acc1):
        n_acc1 = transaction_data.A1
        if validate_account(cur, transaction_data.A1):
            raise HTTPException(status_code=404, detail="INVALID_ACC1")
    else:
        n_acc1 = o_acc1

    if (transaction_data.A2 is not None and transaction_data.A2 != o_acc2):
        n_acc2 = transaction_data.A2
        if validate_account(cur, transaction_data.A2):
            raise HTTPException(status_code=404, detail="INVALID_ACC2")
    else:
        n_acc2 = o_acc2

    if (transaction_data.Remarks and transaction_data.Remarks != o_remarks):
        n_remarks = transaction_data.Remarks
    else:
        n_remarks = o_remarks

    cur.execute("UPDATE Transactions SET A1 = ?, A2 = ?, Amount = ?, Remarks = ? WHERE Id = ?",
                (n_acc1, n_acc2, n_amount, n_remarks, transaction_data.Id))
    cur.execute("""SELECT T.Id, T.Amount, T.Remarks, T.TransactionTime,
        A1.Name AS AcFrom, A2.Name AS AcTo
        FROM Transactions as T
            JOIN Account A1 on A1.Id = T.A1
            JOIN Account A2 on A2.Id = T.A2 
        WHERE T.IsDeleted = FALSE AND T.Id = ?""", (transaction_data.Id, ))
    row = cur.fetchone()
    if (row is None):
        raise HTTPException(status_code=404, detail="TRANS_NOT_FOUND")
    rv = TransactionListItem(
                Amount=row["Amount"],
                Remarks=row["Remarks"],
                Account1=row["AcFrom"],
                Account2=row["AcTo"],
                TransactionTime=row["TransactionTime"],
                Id=row["Id"]
            )
    conn.commit()
    return rv
