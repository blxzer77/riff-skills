def monthly_report(db, month: str):
    return db.execute("SELECT * FROM orders WHERE month = ?", (month,)).fetchall()
