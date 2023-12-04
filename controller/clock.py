from models.employee import Employee
from models.shift import Shift
from flask import json, session
import datetime
from config import app


def process_punch(punch_type, time_str):
    employee = Employee(app.redis.get('employee_no'))
    output = {}
    if punch_type == 'start_shift':
        output = employee.start_shift(time_str, punch_type)
    elif punch_type == 'start_lunch':
        output = employee.start_lunch(time_str, punch_type)
    elif punch_type == 'end_lunch':
        output = employee.end_lunch(time_str, punch_type)
    elif punch_type == 'end_shift':
        output = employee.end_shift(time_str, punch_type)
    return output
