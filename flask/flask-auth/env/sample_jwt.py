from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import datetime

app = Flask(__name__)

app.config['JWT_SECRET_KEY'] = 'thisisasecretkey'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = datetime.timedelta(hours=1)
jwt = JWTManager(app)

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
        }
    }
}

# Helper functions
def check_admin_role(username):
    user = users.get(username)
    return user and user['role']['name'] == 'admin'

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
        access_token = create_access_token(identity=username)
        return jsonify({"message": {"access_token": access_token}}), 200
    return jsonify({"message": "User Not Found"}), 401

@app.route('/api/v1_0/user', methods=['POST'])
@jwt_required()
def create_user():
    current_user = get_jwt_identity()
    if not check_admin_role(current_user):
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
        "role": role
    }
    return jsonify(users[username]), 200

@app.route('/api/v1_0/user/<username>', methods=['GET'])
@jwt_required()
def get_user_info(username):
    user = users.get(username)
    current_user = get_jwt_identity()

    if not user or (users[current_user]['role']['name'] != 'admin' and current_user != username):
        return jsonify({"message": "Permission denied."}), 403

    return jsonify(user), 200

@app.route('/api/v1_0/user/<username>', methods=['PUT'])
@jwt_required()
def update_user_info(username):
    current_user = get_jwt_identity()
    if current_user != username:
        return jsonify({"message": "Permission denied."}), 403

    data = request.get_json()
    user = users.get(username)

    if not user:
        return jsonify({"message": "User not found."}), 400

    user.update(data)
    return jsonify(user), 200

@app.route('/api/v1_0/user/<username>/role', methods=['PATCH'])
@jwt_required()
def update_user_role(username):
    current_user = get_jwt_identity()
    if not check_admin_role(current_user):
        return jsonify({"message": "Permission denied."}), 403

    data = request.get_json()
    new_role = data.get('role')
    user = users.get(username)

    if not user or not new_role:
        return jsonify({"message": "User or role not found."}), 400

    user['role'] = new_role
    return jsonify(user), 200

if __name__ == '__main__':
    app.run(debug=True)


    # AA00DL2XNP
    # AA00DL2XNP