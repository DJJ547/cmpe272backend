from datetime import datetime
from datetime import timedelta
from config import app

from utils import date_convertor

NOT_LATE = 0
LATE = 1
NOT_STARTED = 0
STARTED = 1
ENDED = 2
NOT_LONG = 0
LONG = 1


class Shift:
    def __init__(self, employee_no, assigned_start_time, assigned_end_time):
        self.assigned_start_time = assigned_start_time
        self.assigned_end_time = assigned_end_time
        # open database connection, and fetch data from database
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT * FROM shifts WHERE emp_no = %s AND assign_shift_start = %s AND assign_shift_end = %s", (employee_no, self.assigned_start_time, self.assigned_end_time))
        shift = cur.fetchone()
        cur.close()
        self.shift_id = shift[0]
        self.employee_no = shift[1]
        self.actual_start_time = shift[6]
        self.actual_end_time = shift[9]
        # lunch start and end time will be calculated at the time of initiating a shift
        self.assigned_lunch_start_time = self.calculate_lunch_start_time()
        self.assigned_lunch_end_time = self.calculate_lunch_end_time()
        self.lunch_duration = self.calculate_assign_lunch_duration()
        self.actual_lunch_start_time = shift[7]
        self.actual_lunch_end_time = shift[8]
        self.shift_state = shift[11]
        self.lunch_state = shift[12]
        self.is_shift_late = shift[13]
        self.is_lunch_late = shift[14]
        self.timestamp = shift[15]

    def check_if_is_current_shift(self, time, state):

        if state == 'start_shift' and self.shift_state == NOT_STARTED and -timedelta(minutes=5) <= time - self.assigned_start_time <= timedelta(minutes=30):
            return True
        elif state == 'start_lunch' and self.lunch_state == NOT_STARTED and self.assigned_lunch_start_time <= time <= self.assigned_start_time + self.lunch_duration:
            return True
        elif state == 'end_lunch' and self.lunch_state == STARTED and self.actual_lunch_start_time + self.lunch_duration <= time <= self.assigned_end_time:
            return True
        elif state == 'end_shift' and self.shift_state == STARTED and -timedelta(minutes=5) < time - self.assigned_end_time <= timedelta(minutes=10):
            return True
        else:
            return False

    def calculate_lunch_start_time(self):
        lunch_start_time = None
        # lunchtime will be every four hours
        if self.assigned_end_time - self.assigned_start_time > timedelta(hours=4):
            lunch_start_time = self.assigned_start_time + timedelta(hours=4)
        lunch_start_time_str = date_convertor.convert_datetime_to_string(lunch_start_time)
        # open database connection, and write data to database
        cur = app.mysql.connection.cursor()
        cur.execute(
            "UPDATE shifts SET assign_lunch_start = %s WHERE emp_no = %s AND assign_shift_start = %s",
            (lunch_start_time_str, self.employee_no, self.assigned_start_time))
        app.mysql.connection.commit()
        cur.close()
        return lunch_start_time

    def calculate_lunch_end_time(self):
        lunch_end_time = None
        if self.assigned_lunch_start_time is not None:
            # lunchtime will be every four hours
            if self.assigned_end_time - self.assigned_start_time >= timedelta(hours=8):
                lunch_end_time = self.assigned_lunch_start_time + timedelta(hours=1)
            elif timedelta(hours=4) < self.assigned_end_time - self.assigned_start_time < timedelta(hours=8):
                lunch_end_time = self.assigned_lunch_start_time + timedelta(hours=0.5)
        lunch_end_time_str = date_convertor.convert_datetime_to_string(lunch_end_time)
        # open database connection, and write data to database
        cur = app.mysql.connection.cursor()
        cur.execute(
            "UPDATE shifts SET assign_lunch_end = %s WHERE emp_no = %s AND assign_shift_start = %s",
            (lunch_end_time_str, self.employee_no, self.assigned_start_time))
        app.mysql.connection.commit()
        cur.close()
        return lunch_end_time

    def calculate_assign_lunch_duration(self):
        lunch_duration = None
        if self.assigned_start_time and self.assigned_end_time:
            lunch_duration = self.assigned_end_time - self.assigned_start_time
        lunch_duration_str = date_convertor.convert_datetime_to_string(lunch_duration)
        # open database connection, and fetch data from database
        cur = app.mysql.connection.cursor()
        cur.execute(
            "UPDATE shifts SET lunch_duration = %s WHERE emp_no = %s AND assign_shift_start = %s",
            (lunch_duration_str, self.employee_no, self.assigned_start_time))
        app.mysql.connection.commit()
        cur.close()
        return lunch_duration

    def set_actual_start_time(self, clock_in_time):
        clock_in_time_str = date_convertor.convert_datetime_to_string(clock_in_time)
        error = True
        message = f"shift cannot start at {clock_in_time_str}"

        if self.shift_state == NOT_STARTED and -timedelta(minutes=5) <= clock_in_time - self.assigned_start_time <= timedelta(minutes=5):
            cur = app.mysql.connection.cursor()
            cur.execute("UPDATE shifts SET actual_shift_start = %s, shift_state = %s, is_shift_late = %s WHERE emp_no = %s AND assign_shift_start = %s",
                        (clock_in_time_str, STARTED, NOT_LATE, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"shift started at {clock_in_time_str}"

        elif self.shift_state == NOT_STARTED and timedelta(minutes=5) < clock_in_time - self.assigned_start_time <= timedelta(minutes=30):
            cur = app.mysql.connection.cursor()
            cur.execute("UPDATE shifts SET actual_shift_start = %s, shift_state = %s, is_shift_late = %s WHERE emp_no = %s AND assign_shift_start = %s",
                        (clock_in_time_str, STARTED, LATE, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"shift started late at {clock_in_time_str}"
        return error, message

    def set_actual_end_time(self, clock_out_time):
        clock_out_time_str = date_convertor.convert_datetime_to_string(clock_out_time)
        error = True
        message = f"shift cannot end at {clock_out_time_str}"

        if self.shift_state == STARTED and -timedelta(minutes=5) < clock_out_time - self.assigned_end_time <= timedelta(minutes=10):
            is_long = self.check_if_long_shift(clock_out_time)
            cur = app.mysql.connection.cursor()
            cur.execute(
                "UPDATE shifts SET actual_shift_end = %s, shift_state = %s, is_long_shift = %s WHERE emp_no = %s AND assign_shift_start = %s",
                (clock_out_time_str, ENDED, is_long, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"shift ended at {clock_out_time_str}"
        return error, message

    def check_if_long_shift(self, clock_out_time):
        assign_shift_end_dtime = date_convertor.convert_string_to_datetime(self.assigned_end_time, 'datetime')
        if clock_out_time - self.actual_start_time == assign_shift_end_dtime - self.assigned_start_time:
            return NOT_LONG
        else:
            return LONG

    def set_actual_lunch_start_time(self, lunch_start_time):
        lunch_start_time_str = date_convertor.convert_datetime_to_string(lunch_start_time)
        error = True
        message = f"lunch cannot start at {lunch_start_time_str}"

        if self.lunch_state == NOT_STARTED and self.assigned_lunch_start_time <= lunch_start_time <= self.assigned_lunch_start_time + timedelta(hours=1):
            cur = app.mysql.connection.cursor()
            cur.execute(
                "UPDATE shifts SET actual_lunch_start = %s, lunch_state = %s, is_lunch_late = %s WHERE emp_no = %s AND assign_shift_start = %s",
                (lunch_start_time_str, STARTED, NOT_LATE, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"lunch started at {lunch_start_time_str}"
        elif self.lunch_state == NOT_STARTED and self.assigned_lunch_start_time + timedelta(hours=1) < lunch_start_time <= self.assigned_end_time - self.lunch_duration:
            cur = app.mysql.connection.cursor()
            cur.execute(
                "UPDATE shifts SET actual_lunch_start = %s, lunch_state = %s, is_lunch_late = %s WHERE emp_no = %s AND assign_shift_start = %s",
                (lunch_start_time_str, STARTED, LATE, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"lunch started late at {lunch_start_time_str}"
        return error, message

    def set_actual_lunch_end_time(self, lunch_end_time):
        lunch_end_time_str = date_convertor.convert_datetime_to_string(lunch_end_time)
        error = True
        message = f"lunch cannot end at {lunch_end_time_str}"

        if self.lunch_state == STARTED and self.lunch_duration <= lunch_end_time - self.actual_lunch_start_time <= self.lunch_duration + timedelta(minutes=5):
            cur = app.mysql.connection.cursor()
            cur.execute(
                "UPDATE shifts SET actual_lunch_end = %s, lunch_state = %s, is_long_lunch = %s WHERE emp_no = %s AND assign_shift_start = %s",
                (lunch_end_time_str, ENDED, NOT_LONG, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"lunch ended at {lunch_end_time_str}"
        elif self.lunch_state == STARTED and self.lunch_duration + timedelta(minutes=5) < lunch_end_time <= self.assigned_end_time - self.lunch_duration:
            cur = app.mysql.connection.cursor()
            cur.execute(
                "UPDATE shifts SET actual_lunch_end = %s, lunch_state = %s, is_long_lunch = %s WHERE emp_no = %s AND assign_shift_start = %s",
                (lunch_end_time_str, ENDED, LONG, self.employee_no, self.assigned_start_time))
            app.mysql.connection.commit()
            cur.close()
            error = False
            message = f"lunch ended long at {lunch_end_time_str}"
        return error, message

    def check_shift_state(self):
        return self.shift_state
