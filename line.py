import os
import logging
from flask import Flask, jsonify
import requests
import subprocess

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/check')
def check():
    host = os.environ.get('SPECIFIC_IP')
    api_url = os.environ.get('API_URL')
    
    if not host or not api_url:
        return jsonify({"error": "SPECIFIC_IP or API_URL environment variable is not set"}), 500

    results = {}

    # Ping the server
    try:
        ping_output = subprocess.check_output(['ping', '-c', '4', host], universal_newlines=True)
        results['ping'] = {"success": True, "output": ping_output}
    except subprocess.CalledProcessError as e:
        results['ping'] = {"success": False, "error": str(e), "output": e.output}

    # Check API connection
    try:
        response = requests.get(api_url, timeout=10)
        results['api'] = {
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "content": response.text[:200]  # First 200 characters of the response
        }
    except requests.RequestException as e:
        results['api'] = {"success": False, "error": str(e)}

    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)