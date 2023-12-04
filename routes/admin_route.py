from flask import blueprints, jsonify, request, Response, session, json
from config import app
from models.admin import admin
from datetime import datetime

admin_route = blueprints.Blueprint('admin_route', __name__)

@admin_route.route('/admin/Get_all_users', methods=['GET'])
def get_all_users():
    if request.method == 'GET':
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT emp_no, birth_date, first_name, last_name, gender, hire_date FROM employees Order by emp_no DESC limit 50")
        data = cur.fetchall()
        cur.close()
        
        output = []
        for i in data:
            j ={}
            j['id'] = i[0]
            j['birth_date'] = i[1]
            j['first_name'] = i[2]
            j['last_name'] = i[3]
            j['gender'] = i[4]
            j['hire_date'] = i[5]
            output.append(j)
        
        return Response(json.dumps(output), status=200)

@admin_route.route('/admin/Update_user', methods=['PUT'])
def update_user():
    row = request.get_json()
    birth_date = datetime.strptime(row['birth_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    hire_date = datetime.strptime(row['hire_date'], "%Y-%m-%dT%H:%M:%S.%fZ")
    formatted_birth_date = birth_date.strftime("%Y-%m-%d")
    formatted_hire_date = hire_date.strftime("%Y-%m-%d")
    cur = app.mysql.connection.cursor()
    cur.execute("SELECT emp_no FROM employees where emp_no = %s", (row['id'],))
    user = cur.fetchone()
    cur.execute("SELECT MAX(emp_no) FROM employees")
    max_id = cur.fetchone()[0]
    print(user, max_id)
    if user:
        update_query = """
        UPDATE employees
        SET birth_date = %s, first_name = %s, last_name = %s, gender = %s, hire_date = %s
        WHERE emp_no = %s
        """
        cur.execute(update_query, (formatted_birth_date, row['first_name'], row['last_name'], row['gender'], formatted_hire_date, row['id']))
        message = 'User updated successfully!'
    else:
        password = str('1234')
        cur.execute("""
        INSERT INTO employees (emp_no, birth_date, first_name, last_name, gender, hire_date, password)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (max_id+1, formatted_birth_date, row['first_name'], row['last_name'], row['gender'], formatted_hire_date, password))
        message = 'User added successfully!'
    app.mysql.connection.commit()
    cur.close()
    return Response(json.dumps({'message': message}), status=200)

@admin_route.route('/admin/Delete_user', methods=['DELETE'])
def delete_user():
    row = request.get_json()
    if admin.is_manager(row['id']):
        return Response(json.dumps({'message': 'User is a manager, deletion failed'}), status=200)
    
    cur = app.mysql.connection.cursor()
    delete_query = """
    DELETE FROM employees
    WHERE emp_no = %s
    """
    cur.execute(delete_query, (row['id'],))
    cur.execute("DELETE FROM chat_history WHERE sender = %s or receiver = %s", (row['id'], row['id']))
    app.mysql.connection.commit()
    cur.close()

    return Response(json.dumps({'message': 'User deleted successfully!'}), status=200)