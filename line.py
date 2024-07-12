import os
import logging
from flask import Flask, jsonify
import requests
from flask import request
app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/check_api')
@app.route('/check_api')
def check_api():
    api_url = os.environ.get('API_URL')
    app.logger.debug('Headers: %s', request.headers)
    app.logger.debug('Request Body: %s', request.data)
    app.logger.debug('Request URL: %s', request.url)
    if not api_url:
        app.logger.error("API_URL environment variable is not set")
        return jsonify({"error": "API_URL environment variable is not set"}), 500

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded'  # Optional
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
