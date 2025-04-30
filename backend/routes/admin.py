# backend/routes/admin.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..app      import db
from ..models   import ParkingLot, ParkingSpot

bp = Blueprint("admin", __name__)

def admin_only(fn):
    """Decorator: only allow role=='admin'."""
    from functools import wraps
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != "admin":
            return jsonify({"error":"forbidden"}), 403
        return fn(*args, **kwargs)
    return wrapper

@bp.route("/lots", methods=["GET"])
@login_required
@admin_only
def list_lots():
    lots = ParkingLot.query.all()
    data = []
    for lot in lots:
        available = sum(1 for s in lot.spots if s.status == "A")
        data.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "address": lot.address,
            "pincode": lot.pincode,
            "total_spots": lot.total_spots,
            "available_spots": available
        })
    return jsonify(data), 200

@bp.route("/lots", methods=["POST"])
@login_required
@admin_only
def create_lot():
    payload = request.get_json() or {}
    # required fields
    for f in ("name","price_per_hour","total_spots"):
        if f not in payload:
            return jsonify({"error":f"{f} required"}), 400

    lot = ParkingLot(
        prime_location_name=payload["name"],
        price_per_hour=float(payload["price_per_hour"]),
        address=payload.get("address"),
        pincode=payload.get("pincode"),
        total_spots=int(payload["total_spots"])
    )
    db.session.add(lot)
    db.session.flush()  # assign lot.id
    # auto-generate spots
    for _ in range(lot.total_spots):
        db.session.add(ParkingSpot(lot_id=lot.id))
    db.session.commit()
    return jsonify({"message":"lot created","lot_id":lot.id}), 201

@bp.route("/lots/<int:lot_id>", methods=["PUT"])
@login_required
@admin_only
def update_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    data = request.get_json() or {}
    # update attributes
    if "name" in data:
        lot.prime_location_name = data["name"]
    if "price_per_hour" in data:
        lot.price_per_hour = float(data["price_per_hour"])
    if "address" in data:
        lot.address = data["address"]
    if "pincode" in data:
        lot.pincode = data["pincode"]
    # adjust spot count
    if "total_spots" in data:
        new_total = int(data["total_spots"])
        diff = new_total - lot.total_spots
        if diff > 0:
            for _ in range(diff):
                db.session.add(ParkingSpot(lot_id=lot.id))
        elif diff < 0:
            # remove only available spots
            empties = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").limit(-diff).all()
            if len(empties) < -diff:
                return jsonify({"error":"not enough free spots to remove"}), 400
            for spot in empties:
                db.session.delete(spot)
        lot.total_spots = new_total
    db.session.commit()
    return jsonify({"message":"lot updated"}), 200

@bp.route("/lots/<int:lot_id>", methods=["DELETE"])
@login_required
@admin_only
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    # only delete if all spots free
    if any(s.status == "O" for s in lot.spots):
        return jsonify({"error":"cannot delete: spots occupied"}), 400
    db.session.delete(lot)
    db.session.commit()
    return jsonify({"message":"lot deleted"}), 200

@bp.route("/spots/<int:spot_id>", methods=["DELETE"])
@login_required
@admin_only
def delete_spot(spot_id):
    spot = ParkingSpot.query.get_or_404(spot_id)
    if spot.status != "A":
        return jsonify({"error":"cannot delete occupied spot"}), 400
    db.session.delete(spot)
    db.session.commit()
    return jsonify({"message":"spot deleted"}), 200