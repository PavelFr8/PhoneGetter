from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES
from werkzeug.exceptions import HTTPException

from app.api import module


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    return payload, status_code


def bad_request(message):
    return error_response(400, message)


@module.errorhandler(HTTPException)
def handle_exception(e):
    return error_response(e.code)

@module.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@module.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500