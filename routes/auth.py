from flask import Blueprint, request, Response, jsonify, json, session
import jwt
from config import app
from models.employee import Employee
from models.manager import Manager
from models.admin import Admin
from utils import date_convertor
# authentication routes
from models.admin import admin
auth = Blueprint('auth', __name__)


@auth.route('/auth/login', methods=['POST'])
def login():
    if request.method == 'POST':
        # get user input
        employee_no = request.json['employee_no']
        password = request.json['password']

         # open database connection, and fetch data from database
        cur = app.mysql.connection.cursor()
        cur.execute("""
                          SELECT
                              e.emp_no,
                              e.birth_date,
                              e.first_name,
                              e.last_name,
                              e.gender,
                              e.hire_date,
                              e.profile_pic,
                              e.motto,
                              e.password,
                              d.dept_name,
                              t.title
                          FROM
                              employees e
                          INNER JOIN
                              dept_emp de ON e.emp_no = de.emp_no
                          INNER JOIN
                              departments d ON de.dept_no = d.dept_no
                          INNER JOIN
                              titles t ON e.emp_no = t.emp_no
                          WHERE
                              e.emp_no = %s
                              AND e.password = %s
                              AND de.to_date = (SELECT MAX(de2.to_date) FROM dept_emp de2 WHERE de2.emp_no = e.emp_no)
                              AND t.to_date = (SELECT MAX(t2.to_date) FROM titles t2 WHERE t2.emp_no = e.emp_no)
                          """, (employee_no, password))
        user = cur.fetchone()
        cur.close()

        # check exist or not, the data fetched from database
        if user:
            # add jwt token
            token = jwt.encode({'employee_no': employee_no},
                               app.secret_key, algorithm='HS256')

            employee_no = user[0]
            birthdate = user[1]
            first_name = user[2]
            last_name = user[3]
            gender = user[4]
            hire_date = user[5]
            is_manager = admin.is_manager(employee_no)

            #return the user data fetched from database to frontend
            profile_pic = user[6]
            motto = user[7]
            dept_name = user[9]
            title = user[10]

            cur = app.mysql.connection.cursor()
            cur.execute("SELECT * FROM dept_emp WHERE emp_no = %s", (employee_no,))
            dept_info = cur.fetchone()
            dept_no = dept_info[1]
            from_date = dept_info[2]
            to_date = dept_info[3]

            # load data into redis server side session
            app.redis.set('employee_no', employee_no)
            app.redis.set('first_name', first_name)
            app.redis.set('last_name', last_name)
            app.redis.set('birthdate', date_convertor.convert_datetime_to_string(birthdate))
            app.redis.set('gender', gender)
            app.redis.set('hire_date', date_convertor.convert_datetime_to_string(hire_date))
            app.redis.set('dept_no', dept_no)
            app.redis.set('from_date', date_convertor.convert_datetime_to_string(from_date))
            app.redis.set('to_date', date_convertor.convert_datetime_to_string(to_date))

            # check if he is a manager
            cur.execute("SELECT * FROM dept_manager WHERE emp_no = %s", (employee_no,))
            manager_info = cur.fetchone()
            cur.close()
            state = None
            if manager_info:
                state = 'M'
                dept_no = manager_info[1]
                from_date = manager_info[2]
                to_date = manager_info[3]
                # manager = Manager(employee_no, first_name, last_name, birthdate, gender, hire_date,  dept_no, from_date, to_date)
                app.redis.set('state', state)
            else:
                state = 'E'
                # employee = Employee(employee_no, birthdate, first_name, last_name, gender, hire_date)
                app.redis.set('state', state)

            data = {'employee_no': employee_no, 'first_name': first_name, 'last_name': last_name, 'hire_date': hire_date, 'birthdate': birthdate, 'gender': gender, 
                    'dept_no': dept_no, 'from_date': from_date, 'to_date': to_date, 'state': state, 'profile_pic': profile_pic, 'motto': motto, 'dept_name': dept_name, 
                    'title': title, 'is_manager': is_manager}
            
            response = {'message': 'success', 'error': False, 'data': data, 'token': token}
            #return the user data fetched from database to frontend
            return Response(json.dumps(response), status=200)
        else:
            # return error message to frontend
            return Response(json.dumps({'message': 'Invalid email or password'}), status=401)
        
@auth.route('/auth/logout', methods=['GET'])
def logout():
    if request.method == 'GET':
        app.redis.flushall()
    return Response(json.dumps({'message': 'Successfully logged out'}), status=200)


@auth.route('/auth/changePassword', methods=['POST'])
def change_password():
    emp_no = request.json['emp_no']
    old_password = request.json['currentPassword']
    new_password = request.json['newPassword']
    
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT * FROM employees WHERE emp_no = %s AND password = %s", (emp_no, old_password))
    user = cur.fetchone()
    if user:
        cur = app.mysql.connection.cursor()
        cur.execute("UPDATE employees SET password = %s WHERE emp_no = %s", (new_password, emp_no))
        app.mysql.connection.commit()
        cur.close()
        return Response(json.dumps({'message': 'Password changed successfully'}), status=200)
    else:
        return Response(json.dumps({'message': 'Invalid current password'}), status=401)

""" 
@auth.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        email = request.json['email']
        password = request.json['password']
        name = request.json['name']
        
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email = %s", (email,))
        existingUser = cur.fetchone()

        if existingUser:
            cur.close()
            return jsonify({'message': 'email already registered'})
        else:
            cur.execute("INSERT INTO users (email, password, name) VALUES (%s, %s, %s)", (email, password, name))
            mysql.connection.commit()
            cur.close()

        return Response(json.dumps({'message': 'User registration successfully'}), status=200) """
