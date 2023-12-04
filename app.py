from flask import Flask, \
    render_template, \
    session, \
    Response, \
    jsonify, \
    make_response, \
    request, \
    json
from config import app
from routes.auth import auth
from routes.Clock import clock
from routes.Message import socketio, message
from routes.admin_route import admin_route
from routes.dashboard import dashboard
from routes.setting import setting
from routes.Schedule import schedule

# authentication routes
app.register_blueprint(auth)
app.register_blueprint(clock)
app.register_blueprint(message)
app.register_blueprint(admin_route)
app.register_blueprint(dashboard)
# app.register_blueprint(infoCard)
app.register_blueprint(setting)
app.register_blueprint(schedule)


@app.route('/test')
def test():
    output = 'testing'
    return Response(json.dumps(output), status=200)


if __name__ == '__main__':
    socketio.run(app, debug=True)
