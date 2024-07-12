import os
import logging
from flask import Flask, jsonify, request
import requests

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/check_api')
def check_api():
    api_url = os.environ.get('API_URL')  # Ensure this environment variable is correctly set in Render
    if not api_url:
        app.logger.error("API_URL environment variable is not set")
        return jsonify({"error": "API_URL environment variable is not set"}), 500
    
    full_url = f"{api_url}"  # This is the full API URL you are accessing; make sure it's correct
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Accept': '*/*',
        'Content-Type': 'application/x-www-form-urlencoded'  # Optional, depending on API requirements
    }
    
    # Logging request details for debugging
    app.logger.debug('Request Headers: %s', headers)
    app.logger.debug('Full URL being requested: %s', full_url)

    try:
        response = requests.get(full_url, headers=headers, timeout=10)
        app.logger.debug(f"API response status: {response.status_code}")
        app.logger.debug(f"API response body: {response.text[:500]}")  # Logs the first 500 chars of the response
        
        return jsonify({
            "success": response.status_code == 200,
            "status_code": response.status_code,
            "content": response.text[:200]  # Returns the first 200 characters of the response
        })
    except requests.RequestException as e:
        app.logger.error(f"API request failed: {str(e)}")
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
