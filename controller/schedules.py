from models.employee import Employee
from models.manager import Manager
from models.shift import Shift
from datetime import datetime
from utils import shifts_db, date_convertor
from config import app

def get_all_dept_employees_and_shifts():
    manager = Manager(app.redis.get('employee_no'))
    all_dept_shifts = manager.get_all_dept_shifts_given_dept_no(app.redis.get('dept_no'))
    return all_dept_shifts

def get_self_schedule():
    shifts = shifts_db.get_shifts_from_db(app.redis.get('employee_no'))
    return shifts

def assign_shift(first_name, last_name, start_time, end_time):
    start_time = date_convertor.datetime_to_eight_hour_before(start_time)
    end_time = date_convertor.datetime_to_eight_hour_before(end_time)
    manager = Manager(app.redis.get('employee_no'))
    emp_no = manager.get_employee_no(first_name, last_name)
    if not emp_no:
        output = {'error': True, 'message': 'Employee info is wrong'}
    else:
        manager.assign_shift(emp_no, start_time, end_time)
        output = {'error': False, 'message': 'success'}
    return output
    





