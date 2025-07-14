# backend/routes/user.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..app      import db
from ..models   import ParkingLot, ParkingSpot, Reservation, db
from datetime   import datetime
from sqlalchemy import func

bp = Blueprint("user", __name__)

@bp.route("/lots", methods=["GET"])
@login_required
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
@login_required
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
        user_id=current_user.id,
        parked_at=datetime.utcnow()
    )
    db.session.add(resv)
    db.session.commit()

    return jsonify({
        "message": "spot booked",
        "reservation_id": resv.id,
        "spot_id": spot.id,
        "parked_at": resv.parked_at.isoformat()
    }), 201

@bp.route("/reservations/<int:resv_id>/release", methods=["POST"])
@login_required
def release_reservation(resv_id):
    """
    Release a booked spot.
    """
    resv = Reservation.query.get_or_404(resv_id)
    if resv.user_id != current_user.id or resv.left_at:
        return jsonify({"error":"invalid reservation"}), 400

    resv.left_at = datetime.utcnow()
    resv.calculate_cost()
    resv.spot.status = "A"
    db.session.commit()

    return jsonify({
        "message": "spot released",
        "left_at": resv.left_at.isoformat(),
        "cost": resv.parking_cost
    }), 200

@bp.route("/reservations", methods=["GET"])
@login_required
def list_my_reservations():
    """List all your reservations."""
    resvs = Reservation.query.filter_by(user_id=current_user.id).all()
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
@login_required
def user_summary():
    """
    Return total number of reservations and total spent for current user.
    """
    # 1) total reservations (all, regardless of completed or not)
    total_resv = Reservation.query.filter_by(user_id=current_user.id).count()
    # 2) total spent: sum up parking_cost on any reservation where cost is set
    total_spent = (
        db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0))
        .filter(
            Reservation.user_id == current_user.id,
            Reservation.parking_cost != None
        )
        .scalar()
    )
    # ensure it’s a float for JSON
    return jsonify({
        'total_reservations': total_resv,
        'total_spent': float(total_spent)
    }), 200