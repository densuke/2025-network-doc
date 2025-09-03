from flask import Flask, jsonify, Response
from typing import Dict, List, Any, Union
import json

app: Flask = Flask(__name__)

with open(app.root_path + '/users.json', 'r') as f:
    users: List[Dict[str, Any]] = json.load(f)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int) -> Union[Response, tuple[Response, int]]:
    user: Union[Dict[str, Any], None] = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)
