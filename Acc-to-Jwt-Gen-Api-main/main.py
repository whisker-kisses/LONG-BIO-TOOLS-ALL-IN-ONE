#━━━━━━━━━━━━━━━━━━━
#@watashii_ff
#━━━━━━━━━━━━━━━━━━━
from flask import Flask, jsonify, request
from flask_caching import Cache
from app.utils.response2 import process_token
from colorama import init
import warnings
from urllib3.exceptions import InsecureRequestWarning
import time

# Ignore SSL warnings
warnings.filterwarnings("ignore", category=InsecureRequestWarning)

# Initialize colorama
init(autoreset=True)

# Initialize Flask app
app = Flask(__name__)

cache = Cache(app, config={"CACHE_TYPE": "simple"})  # In-memory cache

@app.route("/")
def home():
    return "JWT Token Generator API is running!"

@app.route("/token", methods=["GET"])
def get_responses():
    key = request.args.get("key")
    access_token = request.args.get("access")
    valid_keys = {"watashii", "faraz"}  # Replace with your actual keys

    if not key or key not in valid_keys:
        return jsonify({"error": "Invalid or missing API key."}), 401

    if access_token:
        response = process_token(access_token)
        return jsonify(response)

    # Bulk retrieval logic removed as per request
    return jsonify({"message": "Bulk retrieval logic has been removed."})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=30326)

