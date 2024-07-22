import os
import logging
import socket
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

def tcp_ping(host, port=80, timeout=5):
    """Attempt to connect to (host, port) and return whether it was successful."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True
    except socket.error as e:
        app.logger.error(f"Failed to connect to {host} on port {port}: {e}")
        return False

@app.route('/ping')
def ping_host():
    host = os.environ.get('SPECIFIC_IP')
    port = 80  # Default to HTTP port; adjust as necessary
    if not host:
        return jsonify({"success": False, "error": "SPECIFIC_IP environment variable is not set"}), 400
    
    if tcp_ping(host, port):
        return jsonify({"success": True, "message": "Successfully connected to the server via TCP."}), 200
    else:
        return jsonify({"success": False, "message": "Failed to connect to the server via TCP."}), 400

@app.route('/icmp_ping')
def icmp_ping():
    host = os.environ.get('SPECIFIC_IP')
    if not host:
        return jsonify({"success": False, "error": "SPECIFIC_IP environment variable is not set"}), 400

    try:
        # Example using ip-api.com
        response = requests.get(f"http://ip-api.com/json/{host}")
        data = response.json()
        if data.get("status") == "success":
            return jsonify({"success": True, "message": f"Successfully pinged {host}.", "data": data}), 200
        else:
            return jsonify({"success": False, "message": f"Ping to {host} failed.", "data": data}), 400
    except requests.RequestException as e:
        app.logger.error(f"ICMP ping to {host} failed: {e}")
        return jsonify({"success": False, "message": f"ICMP ping to {host} failed: {e}"}), 500

@app.route('/check_api/<cid>/<pid>')
def check_api(cid, pid):
    base_api_url = os.environ.get('API_BASE_URL')  # Base URL without the dynamic parts
    if not base_api_url:
        app.logger.error("API_BASE_URL environment variable is not set")
        return jsonify({"error": "API_BASE_URL environment variable is not set"}), 500

    # Construct the full API URL including the dynamic parts
    full_api_url = f"{base_api_url}/status/{cid}/{pid}"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    try:
        app.logger.debug(f"Sending request to API URL: {full_api_url} with headers: {headers}")
        response = requests.get(full_api_url, headers=headers, timeout=10)
        app.logger.debug(f"Request URL: {response.request.url}")
        app.logger.debug(f"Request Headers: {response.request.headers}")
        app.logger.debug(f"Response status code: {response.status_code}")
        app.logger.debug(f"Response body: {response.text[:500]}")
        return jsonify({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "content": response.text[:200]
        })
    except requests.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
