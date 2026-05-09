import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

SECRET            = os.environ.get('OAAT_SECRET', 'Ash@6194')
SOHAIL_API        = 'https://api.oneatatime.io'
ZOHO_EMAIL        = os.environ.get('ZOHO_EMAIL', 'support@oneatatime.io')
ZOHO_APP_PASSWORD = os.environ.get('ZOHO_APP_PASSWORD', '')


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


@app.route('/send-acceptance-email', methods=['OPTIONS'])
def preflight_email():
    return cors(jsonify({}))


@app.route('/send-acceptance-email', methods=['POST'])
def send_acceptance_email():
    if request.headers.get('x-oaat-secret') != SECRET:
        return cors(jsonify({'ok': False, 'error': 'unauthorized'})), 401

    data  = request.get_json(silent=True) or {}
    name  = data.get('name', 'there')
    email = data.get('email', '')

    if not email:
        return cors(jsonify({'ok': False, 'error': 'no email provided'})), 400

    html = f"""<!DOCTYPE html>
<html>
<body style="font-family:sans-serif;font-size:15px;line-height:1.8;color:#333;max-width:600px;margin:0 auto;padding:24px;">
  <p>Hey {name},</p>
  <p>Good news - you made it through ✨</p>
  <p>We've reviewed your profile, and we think you'd be a great fit for One at a Time.</p>
  <p>This is a members-only dating platform built for people who are tired of endless swiping, shallow conversations, and trying to keep up with modern dating culture.</p>
  <p>Here, things move a little differently.</p>
  <p>No swiping.<br>No talking to ten people at once.<br>No pressure to perform.</p>
  <p>Just thoughtful introductions, one at a time.</p>
  <p>Start chatting with our matchmaker on WhatsApp on your registered number — <a href="https://wa.me/918056510101" style="color:#d97706;">click here</a></p>
  <p>We are excited to have you here.</p>
  <p>Best,<br>Team One at a Time 💛</p>
</body>
</html>"""

    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = "You're in ✨ Welcome to One at a Time"
        msg['From']    = ZOHO_EMAIL
        msg['To']      = email
        msg.attach(MIMEText(html, 'html'))

        with smtplib.SMTP_SSL('smtp.zoho.in', 465, timeout=30) as s:
            s.login(ZOHO_EMAIL, ZOHO_APP_PASSWORD)
            s.sendmail(ZOHO_EMAIL, email, msg.as_bytes())

        return cors(jsonify({'ok': True}))
    except Exception as e:
        return cors(jsonify({'ok': False, 'error': str(e)})), 502


@app.route('/health')
def health():
    return jsonify({'ok': True})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
