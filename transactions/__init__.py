from database import get_db
from models import TransactionData, TransactionResponse


def create_transaction(transdata: TransactionData) -> TransactionResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO Transactions (Amount, Remarks, A1, A2) VALUES (? ,? ,?, ?) RETURNING Id",
                    (transdata.Amount, transdata.Remarks, transdata.A1, transdata.A2))
        row_id = cur.fetchone()[0]
        cur.executemany("SELECT Amount FROM Account WHERE Id = ?", [(transdata.A1,), (transdata.A2,)])
        data = cur.fetchall()
        return TransactionResponse(Id=row_id, Bal1=data[0][0], Bal2=data[1][0])
    except Exception as e:
        raise e
