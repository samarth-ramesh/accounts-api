from database import get_db
from models import TransactionData, TransactionResponse


def create_transaction(transdata: TransactionData) -> TransactionResponse:
    try:
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO Transactions (Amount, Remarks, A1, A2) VALUES (? ,? ,?, ?) RETURNING Id",
                    (transdata.Amount, transdata.Remarks, transdata.A1, transdata.A2))
        row_id = cur.fetchone()[0]
        cur.executemany("UPDATE Account SET Amount=Amount+? WHERE Id=?",
                        [(-transdata.Amount, transdata.A1), (transdata.Amount, transdata.A2)])
        # cur.executemany("SELECT Amount FROM Account WHERE Id = ?", [(transdata.A1,), (transdata.A2,)])
        cur.execute("SELECT Id, Amount FROM Account WHERE Id = ? OR Id = ?", (transdata.A1, transdata.A2))
        data = cur.fetchall()
        amounts = {data[0]["Id"]: data[0]["Amount"], data[1]["Id"]: data[1]["Amount"]}
        conn.commit()
        return TransactionResponse(Id=row_id, Bal1=amounts[transdata.A1], Bal2=amounts[transdata.A2])
    except Exception as e:
        raise e
