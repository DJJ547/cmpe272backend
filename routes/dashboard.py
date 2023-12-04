from flask import Blueprint, request, Response, jsonify, json, session
from config import app


dashboard = Blueprint('dashboard', __name__)

@dashboard.route('/dashboard', methods=['GET'])
def get_dashboard_info():
        #open database connection, and fetch data from database
        cur = app.mysql.connection.cursor()
        cur.execute("SELECT * FROM salaries WHERE emp_no = %s", (app.redis.get('employee_no'),))
        salaries_data = cur.fetchall()
        # Prepare data for JSON response
        years = [salary[2].year for salary in salaries_data]
        salaries = [salary[1] for salary in salaries_data]

        # get department name
        cur.execute("SELECT dept_name FROM departments WHERE dept_no = %s", (app.redis.get('dept_no'),))
        dept_name = cur.fetchone()

        # get title
        cur.execute("SELECT title FROM titles WHERE emp_no = %s", (app.redis.get('employee_no'),))
        title_name = cur.fetchone()
        cur.close()

        output = {'years': years, 'salaries': salaries, 'dept_name':dept_name, 'title_name':title_name}
        return Response(json.dumps(output), status=200)
