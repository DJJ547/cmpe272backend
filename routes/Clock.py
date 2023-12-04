from flask import Blueprint, request, Response, jsonify, json, session
from config import app
from controller.clock import process_punch


clock = Blueprint('clock', __name__)


@clock.route('/dashboard/clock', methods=['POST'])
def Clock():
    punch_type = request.json.get('type')
    punch_time = request.json.get('time')
    output = process_punch(punch_type, punch_time)
    return Response(json.dumps(output), status=200)
