from flask import Flask, request, jsonify
from flask_httpauth import HTTPTokenAuth

app = Flask(__name__)
auth = HTTPTokenAuth(scheme='Bearer')

# Sample data storage
users = {
    "admin": {
        "username": "admin",
        "password": "admin_pass",
        "fullname": "Admin User",
        "email": "admin@example.com",
        "role": {
            "name": "admin",
            "access": "all"
        },
        "token": "admin_token"
    }
}

tokens = {"admin_token": "admin"}

# Helper functions
def check_admin_role(token):
    user = get_user_by_token(token)
    return user and user['role']['name'] == 'admin'

def get_user_by_token(token):
    username = tokens.get(token)
    return users.get(username)

@app.route('/api/v1_0/health_check/server', methods=['GET'])
def health_check():
    response = {
        "message": {
            "MongoDB": True,  # Simulated status
            "S3": True  # Simulated status
        }
    }
    return jsonify(response), 200

@app.route('/api/v1_0/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    user = users.get(username)

    if user and user['password'] == password:
        return jsonify({"message": {"access_token": user['token']}}), 200
    return jsonify({"message": "User Not Found"}), 401

@app.route('/api/v1_0/user', methods=['POST'])
@auth.login_required
def create_user():
    if not check_admin_role(auth.current_token()):
        return jsonify({"message": "Permission denied."}), 403
    
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    fullname = data.get('fullname')
    email = data.get('email')
    role = data.get('role')

    if not username or not password or not fullname or not email or not role:
        return jsonify({"message": "Missing required fields."}), 400

    if username in users:
        return jsonify({"message": "User already exists."}), 400

    users[username] = {
        "username": username,
        "password": password,
        "fullname": fullname,
        "email": email,
        "role": role,
        "token": f"{username}_token"
    }
    tokens[f"{username}_token"] = username
    return jsonify(users[username]), 200

@app.route('/api/v1_0/user/<username>', methods=['GET'])
@auth.login_required
def get_user_info(username):
    user = users.get(username)
    current_user = get_user_by_token(auth.current_token())

    if not user or (current_user['role']['name'] != 'admin' and current_user['username'] != username):
        return jsonify({"message": "Permission denied."}), 403

    return jsonify(user), 200

@app.route('/api/v1_0/user/<username>', methods=['PUT'])
@auth.login_required
def update_user_info(username):
    current_user = get_user_by_token(auth.current_token())
    if current_user['username'] != username:
        return jsonify({"message": "Permission denied."}), 403

    data = request.get_json()
    user = users.get(username)

    if not user:
        return jsonify({"message": "User not found."}), 400

    user.update(data)
    return jsonify(user), 200

@app.route('/api/v1_0/user/<username>/role', methods=['PATCH'])
@auth.login_required
def update_user_role(username):
    if not check_admin_role(auth.current_token()):
        return jsonify({"message": "Permission denied."}), 403

    data = request.get_json()
    new_role = data.get('role')
    user = users.get(username)

    if not user or not new_role:
        return jsonify({"message": "User or role not found."}), 400

    user['role'] = new_role
    return jsonify(user), 200

@auth.verify_token
def verify_token(token):
    return token in tokens

if __name__ == '__main__':
    app.run(debug=True)