from flask import Flask, jsonify, send_from_directory, Response
from typing import Dict, List, Any, Union
import json

app: Flask = Flask(__name__)

@app.route('/counter', methods=['GET'])
def counter() -> Response:
    from flask import request, make_response

    count: int = 1
    if 'counter' in request.cookies:
        try:
            count = int(request.cookies.get('counter', '0')) + 1
        except ValueError:
            count = 1

    response: Response = make_response(jsonify({"counter": count}))
    response.set_cookie('counter', str(count), max_age=60*60*24)  # 1日間有効なCookieを設定
    return response
    
with open(app.root_path + '/users.json', 'r', encoding='utf-8') as f:
    users: List[Dict[str, Any]] = json.load(f)

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id: int) -> Union[Response, tuple[Response, int]]:
    user: Union[Dict[str, Any], None] = next((u for u in users if u['id'] == user_id), None)
    if user:
        return jsonify(user)
    else:
        return jsonify({"error": "User not found"}), 404

@app.route('/', methods=['GET'])
def index() -> Response:
    return send_from_directory(app.root_path, 'index.html')

if __name__ == '__main__':
    # 本番環境では debug=False を使用してください
    app.run(debug=True)
