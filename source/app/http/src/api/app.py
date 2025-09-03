from flask import Flask, jsonify, send_from_directory
import json
import os

app = Flask(__name__)

with open('users.json', 'r') as f:
    users = json.load(f)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/', methods=['GET'])
def index():
    return send_from_directory('.', 'index.html')

if __name__ == '__main__':
    app.run(debug=True)
