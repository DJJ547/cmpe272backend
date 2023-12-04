from flask import Blueprint, request, Response, jsonify, json, session
from config import app
from controller import schedules

schedule = Blueprint('schedule', __name__)

@schedule.route('/dashboard/manager/schedule', methods=['GET'])
def get_employee_schedules():
    all_emps_shifts = schedules.get_all_dept_employees_and_shifts()
    return Response(json.dumps(all_emps_shifts), status=200)

@schedule.route('/dashboard/manager/assign', methods=['POST'])
def assign_employee_shift():
    firse_name = request.json.get('firse_name')
    last_name = request.json.get('last_name')
    assign_start_time = request.json.get('assign_start_time')
    assign_end_time = request.json.get('assign_end_time')
    output = schedules.assign_shift(firse_name, last_name, assign_start_time, assign_end_time)
    return Response(json.dumps(output), status=200)

@schedule.route('/dashboard/employee/schedule', methods=['GET'])
def get_schedule():
    output = schedules.get_self_schedule()
    return Response(json.dumps(output), status=200)


