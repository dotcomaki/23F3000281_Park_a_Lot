# backend/routes/admin.py

from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..app      import db
from ..models   import ParkingLot, ParkingSpot, User

bp = Blueprint("admin", __name__, url_prefix="/admin")

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
    db.session.commit()
    return jsonify({"message":"lot updated"}), 200

# GET full lot details (including spots)
@bp.route("/lots/<int:lot_id>", methods=["GET"])
@login_required
@admin_only
def get_lot(lot_id):
    """
    Return full details for a parking lot, including spot statuses.
    """
    lot = ParkingLot.query.get_or_404(lot_id)
    spots = lot.spots
    result = {
        "id": lot.id,
        "prime_location_name": lot.prime_location_name,
        "total_spots": lot.total_spots,
        "available_spots": sum(1 for s in spots if s.status == "A"),
        "spots": [{"id": s.id, "status": s.status} for s in spots]
    }
    return jsonify(result), 200

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

@bp.route('/users', methods=['GET'])
@admin_only
def list_users():
    users = User.query.all()
    payload = []
    for u in users:
        payload.append({
            'id': u.id,
            'username': u.username,
            'email': u.email,
            'role': u.role,
            'registered_at': u.registered_at.isoformat() if u.registered_at else None
        })
    return jsonify(payload)

from ..models import Reservation

@bp.route('/spots/<int:spot_id>', methods=['GET'])
@login_required
@admin_only
def get_spot(spot_id):
    """
    Return the active reservation details for a spot, if occupied.
    """
    reservation = Reservation.query.filter_by(spot_id=spot_id, left_at=None).first()
    if not reservation:
        return jsonify({'error': 'Spot is not currently occupied'}), 404
    user = reservation.user
    return jsonify({
        'reservation_id': reservation.id,
        'user_id': user.id,
        'username': user.username,
        'email': user.email,
        'parked_at': reservation.parked_at.isoformat(),
        'parking_cost': reservation.parking_cost
    }), 200

@bp.route('/search', methods=['GET'])
@admin_only
def search():
    """
    General search for:
      - user_id: returns reservations for that user
      - lot_name: returns parking lots matching name
      - spot_location: returns spots matching address or pincode
      - reservation_id: returns specific reservation
    Query parameters:
      by: one of 'user_id','lot_name','spot_location','reservation_id'
      q: the search string
    """
    by = request.args.get('by', '').strip()
    q = request.args.get('q', '').strip()

    if not by or not q:
        return jsonify({'error': 'Missing search parameters'}), 400

    results = []

    try:
        if by == 'user_id':
            # find reservations for given user_id
            user_id = int(q)
            reservations = Reservation.query.filter_by(user_id=user_id).all()
            for r in reservations:
                lot = r.spot.lot
                results.append({
                    'reservation_id': r.id,
                    'user_id': r.user_id,
                    'username': r.user.username,
                    'spot_id': r.spot_id,
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'parked_at': r.parked_at.isoformat() if r.parked_at else None,
                    'left_at': r.left_at.isoformat() if r.left_at else None,
                    'parking_cost': r.parking_cost
                })

        elif by == 'lot_name':
            # search lots by name substring (case-insensitive)
            lots = ParkingLot.query.filter(ParkingLot.prime_location_name.ilike(f"%{q}%")).all()
            for lot in lots:
                available = sum(1 for s in lot.spots if s.status == "A")
                results.append({
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'address': lot.address,
                    'pincode': lot.pincode,
                    'total_spots': lot.total_spots,
                    'available_spots': available
                })

        elif by == 'spot_location':
            # search spots by lot address or pincode substring
            spots = ParkingSpot.query.join(ParkingLot).filter(
                (ParkingLot.address.ilike(f"%{q}%")) |
                (ParkingLot.pincode.ilike(f"%{q}%"))
            ).all()
            for s in spots:
                lot = s.lot
                results.append({
                    'spot_id': s.id,
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'status': s.status,
                    'address': lot.address,
                    'pincode': lot.pincode
                })

        elif by == 'reservation_id':
            # specific reservation by id
            res_id = int(q)
            r = Reservation.query.get(res_id)
            if r:
                lot = r.spot.lot
                results.append({
                    'reservation_id': r.id,
                    'user_id': r.user_id,
                    'username': r.user.username,
                    'spot_id': r.spot_id,
                    'lot_id': lot.id,
                    'lot_name': lot.prime_location_name,
                    'parked_at': r.parked_at.isoformat() if r.parked_at else None,
                    'left_at': r.left_at.isoformat() if r.left_at else None,
                    'parking_cost': r.parking_cost
                })
        else:
            return jsonify({'error': 'Invalid search category'}), 400

    except ValueError:
        return jsonify({'error': 'Invalid search value'}), 400

    return jsonify(results), 200