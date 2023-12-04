from flask import Blueprint, request, jsonify
from config import app
from models.employee import Employee

setting = Blueprint('setting', __name__)

@setting.route('/setting/updateprofile', methods=['POST'])
def update_profile():
    data = request.json
    employee = Employee(app.redis.get('employee_no'))

    new_motto = data['newMotto']
    new_profile_pic_url = data['newProfilePicUrl']

    print(new_motto)
    print(new_profile_pic_url)
    if employee:
        # Proceed to update motto and profile picture URL
        employee.update_profile(new_motto, new_profile_pic_url)

        return jsonify({'message': 'Profile updated successfully'}), 200
    else:
        return jsonify({'message': 'Employee not found'}), 404
