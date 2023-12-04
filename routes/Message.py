from flask import Blueprint, request, Response, jsonify, json
import jwt
from flask_socketio import SocketIO
from config import app
from flask_cors import CORS

socketio = SocketIO(cors_allowed_origins="http://localhost:3000")
message = Blueprint('message', __name__)


@socketio.on('connect')
def connect():
    print('connected')


@socketio.on('disconnect')
def disconnect():
    print('disconnected')


@socketio.on('message')
def handle_message(data):
    # Save message to MySQL database
    print(data)
    cur = app.mysql.connection.cursor()
    cur.execute("INSERT INTO chat_history (sender, receiver, message) VALUES (%s, %s, %s)",
                (data['sender'], data['receiver'], data['message']))
    app.mysql.connection.commit()
    cur.close()
    # Broadcast message to all connected clients
    socketio.emit('message', data)


@message.route('/chat-history')
def get_chat_history():
    sender = request.args.get('sender')
    receiver = request.args.get('receiver')
    cur = app.mysql.connection.cursor()
    cur.execute("""
        SELECT message, sender
        FROM chat_history
        WHERE (sender = %s AND receiver = %s) OR (sender = %s AND receiver = %s)
        ORDER BY timestamp
    """, (sender, receiver, receiver, sender))
    chat_history = cur.fetchall()
    cur.execute("SELECT profile_pic FROM employees WHERE emp_no = %s", (sender,))
    profile_pic_sender = cur.fetchone()[0]
    cur.execute("SELECT profile_pic FROM employees WHERE emp_no = %s", (receiver,))
    profile_pic_receiver = cur.fetchone()[0]
    cur.close()
    output = {'chat_history': chat_history, 'profile_pic_sender': profile_pic_sender,
              'profile_pic_receiver': profile_pic_receiver}
    
    return json.dumps(output)


@message.route('/employee-search')
def employee_search():
    search = request.args.get('query', '')
    cur = app.mysql.connection.cursor()
    cur.execute(""" SELECT emp_no, first_name, last_name, profile_pic FROM employees WHERE first_name LIKE %s OR last_name LIKE %s OR emp_no LIKE %s LIMIT 20 """,
                ('%'+search + '%', '%'+search + '%', '%'+search + '%'))
    result = cur.fetchall()
    cur.close()
    return json.dumps(result)


@message.route('/recent-contacts')
def recent_contacts():
    emp_no = request.args.get('employee_no')
    cur = app.mysql.connection.cursor()
    cur.execute(""" SELECT sub.sender, sub.receiver
        FROM (
        SELECT DISTINCT sender, receiver
        FROM chat_history
        WHERE sender = %s OR receiver = %s
        ) AS sub
        JOIN chat_history ch ON ch.sender = sub.sender AND ch.receiver = sub.receiver
        ORDER BY ch.timestamp""", (emp_no, emp_no))
    result = cur.fetchall()
    if len(result) == 0:
        return json.dumps([])

    emp_no = int(emp_no)
    distinct_numbers = []
    for sender, receiver in result:
        if sender != emp_no and sender not in distinct_numbers:
            distinct_numbers.append(sender)
        if receiver != emp_no and receiver not in distinct_numbers:
            distinct_numbers.append(receiver)
    ordered_numbers = distinct_numbers[::-1][:20]

    order = ', '.join(map(str, ordered_numbers))
    cur.execute(f""" SELECT emp_no, first_name, last_name FROM employees WHERE emp_no IN %s ORDER BY FIELD(emp_no, {order}) """, (tuple(ordered_numbers),))
    result = cur.fetchall()
    cur.close()
    
    return json.dumps(result)


socketio.init_app(app)
