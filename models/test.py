import datetime
from datetime import timedelta
from employee import Employee
from shift import Shift


def main():
    # Datetime attributes in order: hour, minute, second, microsecond, and tzinfo.

    # first shift on 10/27 from 5pm to 11pm
    first_shift_start_time = datetime.datetime(2023, 10, 27, 17, 00)
    first_shift_end_time = datetime.datetime(2023, 10, 27, 23, 00)
    first_shift = Shift(first_shift_start_time, first_shift_end_time)
    # second shift on 10/28 from 9am to 7pm
    second_shift_start_time = datetime.datetime(2023, 10, 28, 9, 00)
    second_shift_end_time = datetime.datetime(2023, 10, 28, 19, 00)
    second_shift = Shift(second_shift_start_time, second_shift_end_time)
    shifts = [first_shift, second_shift]

    # Employee attributes in order: employee_no, first_name, last_name, birthdate, gender, hire_date, shifts
    # em1 = Employee(1, 'David', 'Dai', datetime.datetime(1994, 5, 20), 'M', datetime.datetime(2023, 9, 10), shifts)

    # try clock in 6 mins early to the first shift
    # clock_in_time = datetime.datetime(2023, 10, 27, 16, 54)
    # em1.start_shift(clock_in_time)
    # em1.shifts[0].print_all_shift_info()

    # try clock in 12 mins late to the first shift
    # clock_in_time = datetime.datetime(2023, 10, 27, 17, 12)
    # em1.start_shift(clock_in_time)
    # em1.shifts[0].print_all_shift_info()

    # try clock in 35 mins late to the first shift
    # clock_in_time = datetime.datetime(2023, 10, 27, 17, 35)
    # em1.start_shift(clock_in_time)
    # em1.shifts[0].print_all_shift_info()

    em1 = Employee(1, 'David', 'Dai', datetime.datetime(1994, 5, 20), 'M', datetime.datetime(2023, 9, 10), shifts)
    print(em1)

if __name__ == '__main__':
    main()
