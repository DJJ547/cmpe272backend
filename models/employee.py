from datetime import datetime
from datetime import timedelta
from config import app

from models.shift import Shift
from utils import date_convertor, shifts_db


class Employee:
    def __init__(self, employee_no):
        self.employee_no = employee_no
        self.first_name = app.redis.get('first_name')
        self.last_name = app.redis.get('last_name')
        self.birthdate = app.redis.get('birthdate')
        self.gender = app.redis.get('gender')
        self.hire_date = app.redis.get('hire_date')
        self.title = app.redis.get('title')
        self.from_date = app.redis.get('from_date')

    def start_shift(self, clock_in_time_str, punch_type):
        shifts = shifts_db.get_shifts_from_db_to_list(self.employee_no)
        clock_in_time_dtime = date_convertor.convert_string_to_datetime(clock_in_time_str, 'datetime')
        response = {'error': True, 'message': f'shift cannot start at {clock_in_time_str}'}
        # loop thru each shift and find the current one
        for shift in shifts:
            if shift.check_if_is_current_shift(clock_in_time_dtime, punch_type):
                print('is current')
                result = shift.set_actual_start_time(clock_in_time_dtime)
                response['error'] = result[0]
                response['message'] = result[1]
        return response

    def end_shift(self, clock_out_time_str, punch_type):
        shifts = shifts_db.get_shifts_from_db_to_list(self.employee_no)
        clock_out_time_dtime = date_convertor.convert_string_to_datetime(clock_out_time_str, 'datetime')
        response = {'error': True, 'message': f'shift cannot end at {clock_out_time_str}'}
        # loop thru each shift and find the current one
        for shift in shifts:
            if shift.check_if_is_current_shift(clock_out_time_dtime, punch_type):
                result = shift.set_actual_end_time(clock_out_time_dtime)
                response['error'] = result[0]
                response['message'] = result[1]
        return response

    def start_lunch(self, lunch_start_time_str, punch_type):
        shifts = shifts_db.get_shifts_from_db_to_list(self.employee_no)
        lunch_start_time_dtime = date_convertor.convert_string_to_datetime(lunch_start_time_str, 'datetime')
        response = {'error': True, 'message': f'lunch cannot start at {lunch_start_time_str}'}
        # loop thru each shift and find the current one
        for shift in shifts:
            if shift.check_if_is_current_shift(lunch_start_time_dtime, punch_type):
                result = shift.set_actual_lunch_start_time(lunch_start_time_dtime)
                response['error'] = result[0]
                response['message'] = result[1]
        return response

    def end_lunch(self, lunch_end_time_str, punch_type):
        shifts = shifts_db.get_shifts_from_db_to_list(self.employee_no)
        lunch_end_time_dtime = date_convertor.convert_string_to_datetime(lunch_end_time_str, 'datetime')
        response = {'error': True, 'message': f'lunch cannot end at {lunch_end_time_str}'}
        # loop thru each shift and find the current one
        for shift in shifts:
            if shift.check_if_is_current_shift(lunch_end_time_dtime, punch_type):
                result = shift.set_actual_lunch_end_time(lunch_end_time_dtime)
                response['error'] = result[0]
                response['message'] = result[1]
        return response

    def update_profile(self, motto, profile_pic_url):
        conn = app.mysql.connection
        cur = conn.cursor()
        try:
            cur.execute("UPDATE employees SET motto = %s, profile_pic = %s WHERE emp_no = %s",
                        (motto, profile_pic_url, self.employee_no))
            conn.commit()
            return {'error': False, 'message': 'Profile updated successfully'}
        except Exception as e:
            conn.rollback()
            return {'error': True, 'message': str(e)}
        finally:
            cur.close()