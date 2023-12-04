from config import app
from models.shift import Shift

def get_shifts_from_db_to_list(employee_no):
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * FROM shifts WHERE emp_no = %s", (employee_no,))
    db_shifts = cur.fetchall()
    cur.close()
    print(db_shifts)
    shifts = []
    if db_shifts:
        for db_shift in db_shifts:
            shifts.append(Shift(db_shift[1], db_shift[2], db_shift[5]))
    return shifts

def get_shifts_from_db(employee_no):
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * FROM shifts WHERE emp_no = %s", (employee_no,))
    db_shifts = cur.fetchall()
    cur.close()
    return db_shifts
