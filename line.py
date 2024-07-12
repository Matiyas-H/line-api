import os
import logging
from flask import Flask, jsonify, request
import requests
import subprocess
import socket
import traceback

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
    try:
        specific_ip = os.environ.get('SPECIFIC_IP')
        if not specific_ip:
            app.logger.error("SPECIFIC_IP environment variable is not set")
            return jsonify({"error": "SPECIFIC_IP environment variable is not set"}), 500
        
        results = {}
        
        # Ping
        try:
            ping_output = subprocess.check_output(['ping', '-c', '4', '-W', '5', specific_ip], universal_newlines=True, stderr=subprocess.STDOUT)
            results['ping'] = {"success": True, "output": ping_output}
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Ping failed: {str(e)}")
            results['ping'] = {"success": False, "error": str(e), "output": e.output}
        except Exception as e:
            app.logger.error(f"Unexpected error during ping: {str(e)}")
            results['ping'] = {"success": False, "error": str(e)}

        # Traceroute
        try:
            traceroute_output = subprocess.check_output(['traceroute', '-m', '15', specific_ip], universal_newlines=True, stderr=subprocess.STDOUT)
            results['traceroute'] = {"success": True, "output": traceroute_output}
        except subprocess.CalledProcessError as e:
            app.logger.error(f"Traceroute failed: {str(e)}")
            results['traceroute'] = {"success": False, "error": str(e), "output": e.output}
        except Exception as e:
            app.logger.error(f"Unexpected error during traceroute: {str(e)}")
            results['traceroute'] = {"success": False, "error": str(e)}

        # TCP connection test
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            tcp_result = sock.connect_ex((specific_ip, 80))
            if tcp_result == 0:
                results['tcp_connection'] = {"success": True, "message": "Port 80 is open"}
            else:
                results['tcp_connection'] = {"success": False, "message": f"Port 80 is closed or filtered. Error code: {tcp_result}"}
        except Exception as e:
            app.logger.error(f"TCP connection test failed: {str(e)}")
            results['tcp_connection'] = {"success": False, "error": str(e)}
        finally:
            sock.close()
        
        # DNS lookup
        try:
            dns_info = socket.gethostbyaddr(specific_ip)
            results['dns_lookup'] = {"success": True, "hostname": dns_info[0], "aliases": dns_info[1], "ip_addresses": dns_info[2]}
        except socket.herror as e:
            app.logger.error(f"DNS lookup failed: {str(e)}")
            results['dns_lookup'] = {"success": False, "error": str(e)}
        except Exception as e:
            app.logger.error(f"Unexpected error during DNS lookup: {str(e)}")
            results['dns_lookup'] = {"success": False, "error": str(e)}
        
        app.logger.info(f"Connectivity test results for {specific_ip}: {results}")
        return jsonify(results)
    except Exception as e:
        app.logger.error(f"Unexpected error in ping_specific_ip: {str(e)}")
        app.logger.error(traceback.format_exc())
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500



if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)