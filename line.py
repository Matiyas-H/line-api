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
        # Example third-party ping API (you need to find a suitable one)
        response = requests.get(f"https://api.ping.pe/{host}")
        data = response.json()
        if response.status_code == 200 and data.get("success"):
            return jsonify({"success": True, "message": f"Successfully pinged {host}.", "data": data}), 200
        else:
            return jsonify({"success": False, "message": f"Ping to {host} failed.", "data": data}), 400
    except requests.RequestException as e:
        app.logger.error(f"ICMP ping to {host} failed: {e}")
        return jsonify({"success": False, "message": f"ICMP ping to {host} failed: {e}"}), 500

@app.route('/check_api')
def check_api():
    api_url = os.environ.get('API_URL')
    if not api_url:
        app.logger.error("API_URL environment variable is not set")
        return jsonify({"error": "API_URL environment variable is not set"}), 500

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    try:
        app.logger.debug(f"Sending request to API URL: {api_url} with headers: {headers}")
        response = requests.get(api_url, headers=headers, timeout=10)
        app.logger.debug(f"API response status: {response.status_code}")
        app.logger.debug(f"API response body: {response.text[:500]}")
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




# import os
# import logging
# import socket
# from flask import Flask, jsonify, request
# import requests

# try:
#     from ping3 import ping, PingError
# except ImportError:
#     from ping3 import ping
#     PingError = None

# app = Flask(__name__)
# logging.basicConfig(level=logging.DEBUG)

# def tcp_ping(host, port=80, timeout=5):
#     """Attempt to connect to (host, port) and return whether it was successful."""
#     try:
#         sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         sock.settimeout(timeout)
#         sock.connect((host, port))
#         sock.close()
#         return True
#     except socket.error as e:
#         app.logger.error(f"Failed to connect to {host} on port {port}: {e}")
#         return False

# @app.route('/ping')
# def ping_host():
#     host = os.environ.get('SPECIFIC_IP')
#     port = 80  # Default to HTTP port; adjust as necessary
#     if not host:
#         return jsonify({"success": False, "error": "SPECIFIC_IP environment variable is not set"}), 400
    
#     if tcp_ping(host, port):
#         return jsonify({"success": True, "message": "Successfully connected to the server via TCP."}), 200
#     else:
#         return jsonify({"success": False, "message": "Failed to connect to the server via TCP."}), 400

# @app.route('/icmp_ping')
# def icmp_ping():
#     host = os.environ.get('SPECIFIC_IP')
#     if not host:
#         return jsonify({"success": False, "error": "SPECIFIC_IP environment variable is not set"}), 400

#     try:
#         response = ping(host, timeout=2)  # Adjust timeout as necessary
#         if response is not None:
#             return jsonify({"success": True, "message": f"Successfully pinged {host} with response time {response} ms."}), 200
#         else:
#             return jsonify({"success": False, "message": f"Ping to {host} failed."}), 400
#     except Exception as e:
#         app.logger.error(f"ICMP ping to {host} failed: {e}")
#         return jsonify({"success": False, "message": f"ICMP ping to {host} failed: {e}"}), 500

# @app.route('/check_api')
# def check_api():
#     api_url = os.environ.get('API_URL')
#     if not api_url:
#         app.logger.error("API_URL environment variable is not set")
#         return jsonify({"error": "API_URL environment variable is not set"}), 500

#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
#         'Accept': '*/*',
#         'Content-Type': 'application/x-www-form-urlencoded'
#     }

#     try:
#         app.logger.debug(f"Sending request to API URL: {api_url} with headers: {headers}")
#         response = requests.get(api_url, headers=headers, timeout=10)
#         app.logger.debug(f"API response status: {response.status_code}")
#         app.logger.debug(f"API response body: {response.text[:500]}")
#         return jsonify({
#             "success": response.status_code == 200,
#             "status_code": response.status_code,
#             "content": response.text[:200]
#         })
#     except requests.RequestException as e:
#         app.logger.error(f"API request failed: {str(e)}")
#         return jsonify({"success": False, "error": str(e)}), 500

# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)
