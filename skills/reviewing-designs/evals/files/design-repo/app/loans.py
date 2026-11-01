from datetime import date, timedelta

LOAN_DAYS = 21


def lend(db, book_id: int, member_id: int, today: date | None = None) -> dict:
    today = today or date.today()
    row = db.execute("SELECT on_loan FROM books WHERE id = ?", (book_id,)).fetchone()
    if row is None or row[0]:
        raise ValueError("book not available")
    due = today + timedelta(days=LOAN_DAYS)
    db.execute("UPDATE books SET on_loan = 1 WHERE id = ?", (book_id,))
    db.execute("INSERT INTO loans (book_id, member_id, due) VALUES (?, ?, ?)",
               (book_id, member_id, due.isoformat()))
    return {"bookId": book_id, "memberId": member_id, "dueDate": due.isoformat()}
