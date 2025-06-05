# backend/routes/auth.py

from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from ..app    import db
from ..models import User

bp = Blueprint("auth", __name__)

@bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    # ensure required fields
    if not all(k in data for k in ("username","email","password")):
        return jsonify({"error":"username, email and password required"}), 400

    # check uniqueness
    if User.query.filter((User.username==data["username"]) | (User.email==data["email"])).first():
        return jsonify({"error":"username or email already taken"}), 400

    # create user
    user = User(username=data["username"], email=data["email"])
    user.set_password(data["password"])
    db.session.add(user)
    db.session.commit()
    return jsonify({"message":"user registered"}), 201

@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    user = User.query.filter_by(username=data.get("username")).first()
    if user is None or not user.check_password(data.get("password","")):
        return jsonify({"error":"invalid credentials"}), 401

    login_user(user)
    return jsonify({"message":"logged in", "role": user.role}), 200

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message":"logged out"}), 200

@bp.route("/me", methods=["GET"])
@login_required
def me():
    return jsonify({
        "id": current_user.id,
        "username": current_user.username,
        "email": current_user.email,
        "role": current_user.role
    }), 200


# Update profile route
@bp.route("/profile", methods=["PUT"])
@login_required
def update_profile():
    """
    Updates current user's username, email, and optional password.
    """
    data = request.get_json() or {}

    username = data.get("username", "").strip()
    email = data.get("email", "").strip()
    new_password = data.get("password", "")

    # Validate username
    if not username or len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400

    # Validate email
    if not email or "@" not in email:
        return jsonify({"error": "A valid email is required."}), 400

    # Check for username/email uniqueness (excluding current user)
    existing = User.query.filter(User.id != current_user.id, User.username == username).first()
    if existing:
        return jsonify({"error": "Username already taken."}), 409

    existing = User.query.filter(User.id != current_user.id, User.email == email).first()
    if existing:
        return jsonify({"error": "Email already registered."}), 409

    # If password provided, validate length and update
    if new_password:
        if len(new_password) < 8:
            return jsonify({"error": "Password must be at least 8 characters."}), 400
        current_user.password_hash = generate_password_hash(new_password)

    # Update username and email
    current_user.username = username
    current_user.email = email

    db.session.commit()
    return jsonify({"message": "Profile updated successfully."}), 200