import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET = os.environ.get('OAAT_SECRET', 'Ash@6194')
SOHAIL_API = 'https://api.oneatatime.io'


def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, x-oaat-secret'
    return response


@app.route('/admin/verify/<phone>', methods=['OPTIONS'])
def preflight(phone):
    return cors(jsonify({}))


@app.route('/admin/verify/<phone>', methods=['POST'])
def proxy_verify(phone):
    if request.headers.get('x-oaat-secret') != SECRET:
        return cors(jsonify({'ok': False, 'error': 'unauthorized'})), 401

    data = request.get_json(silent=True) or {}

    try:
        r = requests.post(
            f'{SOHAIL_API}/admin/verify/{phone}',
            json=data,
            timeout=15
        )
        return cors(jsonify(r.json())), r.status_code
    except Exception as e:
        return cors(jsonify({'ok': False, 'error': str(e)})), 502


@app.route('/admin/verify/<phone>/reset', methods=['OPTIONS'])
def preflight_reset(phone):
    return cors(jsonify({}))


@app.route('/admin/verify/<phone>/reset', methods=['POST'])
def proxy_reset(phone):
    if request.headers.get('x-oaat-secret') != SECRET:
        return cors(jsonify({'ok': False, 'error': 'unauthorized'})), 401

    try:
        r = requests.post(
            f'{SOHAIL_API}/admin/verify/{phone}/reset',
            timeout=15
        )
        return cors(jsonify(r.json())), r.status_code
    except Exception as e:
        return cors(jsonify({'ok': False, 'error': str(e)})), 502


@app.route('/health')
def health():
    return jsonify({'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
