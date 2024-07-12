import os
from flask import Flask, jsonify
import requests

app = Flask(__name__)

@app.route('/check')
def check_api():
    api_url = os.environ.get('API_URL')
    if not api_url:
        return jsonify({"error": "API_URL is not set in environment variables", "is_successful": False}), 500

    try:
        response = requests.get(api_url, timeout=10)
        return jsonify({
            "status_code": response.status_code,
            "is_successful": response.status_code == 200
        })
    except requests.RequestException as e:
        return jsonify({
            "error": str(e),
            "is_successful": False
        }), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)