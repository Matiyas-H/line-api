import os
import logging
from flask import Flask, jsonify, request
import requests
import subprocess

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route('/check')
def check_api():
    api_url = os.environ.get('API_URL')
    if not api_url:
        return jsonify({"error": "API_URL is not set in environment variables", "is_successful": False}), 500

    try:
        # Log the request details
        app.logger.info(f"Sending request to: {api_url}")
        app.logger.info(f"Request headers: {dict(request.headers)}")

        # Make the request
        response = requests.get(api_url, timeout=10)

        # Log the response details
        app.logger.info(f"Response status code: {response.status_code}")
        app.logger.info(f"Response headers: {dict(response.headers)}")
        app.logger.info(f"Response content: {response.text}")

        return jsonify({
            "status_code": response.status_code,
            "is_successful": response.status_code == 200,
            "response_headers": dict(response.headers),
            "response_content": response.text
        })
    except requests.RequestException as e:
        app.logger.error(f"Request failed: {str(e)}")
        return jsonify({
            "error": str(e),
            "is_successful": False
        }), 500

@app.route('/ip')
def get_ip():
    return jsonify({
        "remote_addr": request.remote_addr,
        "x_forwarded_for": request.headers.get('X-Forwarded-For', None)
    })


@app.route('/ping-specific-ip')
def ping_specific_ip():
    specific_ip = os.environ.get('SPECIFIC_IP')
    if not specific_ip:
        return jsonify({"error": "SPECIFIC_IP environment variable is not set"}), 500
    
    try:
        output = subprocess.check_output(['ping', '-c', '4', specific_ip], universal_newlines=True)
        app.logger.info(f"Ping to {specific_ip} successful. Output: {output}")
        return jsonify({"success": True, "ip": specific_ip, "output": output})
    except subprocess.CalledProcessError as e:
        app.logger.error(f"Ping to {specific_ip} failed. Error: {str(e)}")
        return jsonify({"success": False, "ip": specific_ip, "error": str(e), "output": e.output})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)