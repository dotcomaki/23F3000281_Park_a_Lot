# backend/routes/user.py

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db, cache
from ..models   import ParkingLot, ParkingSpot, Reservation
from datetime   import datetime
from sqlalchemy import func

bp = Blueprint("user", __name__)

@bp.route("/lots", methods=["GET"])
@jwt_required()
@cache.cached(timeout=60, key_prefix="user_list_lots")
def list_lots():
    """Return all lots with count of available spots."""
    lots = ParkingLot.query.all()
    result = []
    for lot in lots:
        avail = sum(1 for s in lot.spots if s.status == "A")
        result.append({
            "id": lot.id,
            "name": lot.prime_location_name,
            "price_per_hour": lot.price_per_hour,
            "available_spots": avail
        })
    return jsonify(result), 200

@bp.route("/reservations", methods=["POST"])
@jwt_required()
def create_reservation():
    """
    Book first available spot in given lot.
    JSON body: { "lot_id": 1 }
    """
    data = request.get_json() or {}
    lot = ParkingLot.query.get_or_404(data.get("lot_id"))
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status="A").first()
    if not spot:
        return jsonify({"error":"no spots available"}), 400

    # occupy it and create reservation
    spot.status = "O"
    resv = Reservation(
        spot_id=spot.id,
        user_id=get_jwt_identity(),
        parked_at=datetime.utcnow()
    )
    db.session.add(resv)
    db.session.commit()
    # Invalidate caches
    cache.delete('user_list_lots')
    cache.delete('user_summary')

    return jsonify({
        "message": "spot booked",
        "reservation_id": resv.id,
        "spot_id": spot.id,
        "parked_at": resv.parked_at.isoformat()
    }), 201

@bp.route("/reservations/<int:resv_id>/release", methods=["POST"])
@jwt_required()
def release_reservation(resv_id):
    """
    Release a booked spot.
    """
    resv = Reservation.query.get_or_404(resv_id)
    uid = get_jwt_identity()
    if resv.user_id != uid or resv.left_at:
        return jsonify({"error":"invalid reservation"}), 400

    resv.left_at = datetime.utcnow()
    resv.calculate_cost()
    resv.spot.status = "A"
    db.session.commit()
    # Invalidate caches
    cache.delete('user_list_lots')
    cache.delete('user_summary')

    return jsonify({
        "message": "spot released",
        "left_at": resv.left_at.isoformat(),
        "cost": resv.parking_cost
    }), 200

@bp.route("/reservations", methods=["GET"])
@jwt_required()
def list_my_reservations():
    """List all your reservations."""
    uid = get_jwt_identity()
    resvs = Reservation.query.filter_by(user_id=uid).all()
    output = []
    for r in resvs:
        output.append({
            "id": r.id,
            "lot_id": r.spot.lot_id,
            "spot_id": r.spot_id,
            "parked_at": r.parked_at.isoformat(),
            "left_at": r.left_at.isoformat() if r.left_at else None,
            "cost": r.parking_cost
        })
    return jsonify(output), 200

@bp.route('/summary', methods=['GET'])
@jwt_required()
@cache.cached(timeout=60, key_prefix="user_summary")
def user_summary():
    """
    Return total number of reservations and total spent for current user.
    """
    uid = get_jwt_identity()
    # 1) total reservations (all, regardless of completed or not)
    total_resv = Reservation.query.filter_by(user_id=uid).count()
    # 2) total spent: sum up parking_cost on any reservation where cost is set
    total_spent = (
        db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0))
        .filter(
            Reservation.user_id == uid,
            Reservation.parking_cost != None
        )
        .scalar()
    )
    # ensure it’s a float for JSON
    return jsonify({
        'total_reservations': total_resv,
        'total_spent': float(total_spent)
    }), 200