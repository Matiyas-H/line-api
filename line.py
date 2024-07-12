import os
import logging
from flask import Flask, jsonify
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/check_api')
def check_api():
    api_url = os.environ.get('API_URL')
    
    if not api_url:
        app.logger.error("API_URL environment variable is not set")
        return jsonify({"error": "API_URL environment variable is not set"}), 500

    try:
        app.logger.debug(f"Sending request to API URL: {api_url}")
        response = requests.get(api_url, timeout=10)
        app.logger.debug(f"API response status: {response.status_code}")
        app.logger.debug(f"API response body: {response.text[:500]}")  # Logs first 500 chars of the response
        return jsonify({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "content": response.text[:200]  # First 200 characters of the response
        })
    except requests.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
