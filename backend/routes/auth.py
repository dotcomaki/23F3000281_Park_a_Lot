from flask import Blueprint, request, jsonify
from flask_login import current_user
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from ..app    import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    if not all(k in data for k in ("username","email","password")):
        return jsonify({"error":"username, email and password required"}), 400

    if User.query.filter((User.username==data["username"]) | (User.email==data["email"])).first():
        return jsonify({"error":"username or email already taken"}), 400

    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"user registered"}), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    username = data.get("username") or ""
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        return jsonify({"error": "invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    return jsonify({
        "access_token": access_token,
        "role": user.role
    }), 200

@bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    return jsonify({"message":"logged out"}), 200

@bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role
    }), 200


@bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Updates current user's username, email, and optional password.
    """
    data = request.get_json() or {}

    user_id = int(get_jwt_identity())
    user = User.query.get_or_404(user_id)

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    new_password = data.get("password", "")

    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400

    if not email or "@" not in email:
        return jsonify({"error": "A valid email is required."}), 400

    existing = User.query.filter(User.id != user.id, User.username == username).first()
    if existing:
        return jsonify({"error": "Username already taken."}), 409

    existing = User.query.filter(User.id != user.id, User.email == email).first()
    if existing:
        return jsonify({"error": "Email already registered."}), 409

    if new_password:
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400
        user.password_hash = generate_password_hash(new_password)

    user.username = username
    user.email = email

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200