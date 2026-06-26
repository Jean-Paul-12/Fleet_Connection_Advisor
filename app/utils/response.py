from flask import jsonify


def success_response(data=None, status_code: int = 200):
    payload = {"success": True, "data": data}
    return jsonify(payload), status_code


def error_response(message: str, error_code: str, status_code: int, details=None):
    payload = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
            "details": details or {},
        },
    }
    return jsonify(payload), status_code
