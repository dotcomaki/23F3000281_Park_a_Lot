from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..extensions import db, cache
from ..models   import ParkingLot, ParkingSpot, Reservation
from datetime   import datetime
from sqlalchemy import func
from flask import current_app

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

    spot.status = "O"
    resv = Reservation(
        spot_id=spot.id,
        user_id=int(get_jwt_identity()),
        parked_at=datetime.utcnow()
    )
    db.session.add(resv)
    db.session.commit()
    cache.delete('user_list_lots')
    cache.delete('user_summary')

    return jsonify({
        "message": "spot booked",
        "reservation_id": resv.id,
        "spot_id": spot.id,
        "parked_at": resv.parked_at.isoformat() + 'Z'
    }), 201

@bp.route("/reservations/<int:resv_id>/release", methods=["POST"])
@jwt_required()
def release_reservation(resv_id):
    """
    Release a booked spot.
    """
    resv = Reservation.query.get_or_404(resv_id)
    uid = int(get_jwt_identity())
    if resv.user_id != uid or resv.left_at:
        return jsonify({"error":"invalid reservation"}), 400

    resv.left_at = datetime.utcnow()
    resv.calculate_cost()
    resv.spot.status = "A"
    db.session.commit()
    cache.delete('user_list_lots')
    cache.delete('user_summary')

    return jsonify({
        "message": "spot released",
        "left_at": resv.left_at.isoformat() + 'Z',
        "cost": resv.parking_cost
    }), 200

@bp.route("/reservations", methods=["GET"])
@jwt_required()
def list_my_reservations():
    """List all your reservations."""
    uid = int(get_jwt_identity())
    resvs = Reservation.query.filter_by(user_id=uid).all()
    output = []
    for r in resvs:
        output.append({
            "id": r.id,
            "lot_id": r.spot.lot_id,
            "spot_id": r.spot_id,
            "parked_at": r.parked_at.isoformat() + 'Z' if r.parked_at else None,
            "left_at": r.left_at.isoformat() + 'Z' if r.left_at else None,
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
    uid = int(get_jwt_identity())
    total_resv = Reservation.query.filter_by(user_id=uid).count()
    total_spent = (
        db.session.query(func.coalesce(func.sum(Reservation.parking_cost), 0))
        .filter(
            Reservation.user_id == uid,
            Reservation.parking_cost != None
        )
        .scalar()
    )
    return jsonify({
        'total_reservations': total_resv,
        'total_spent': float(total_spent)
    }), 200

@bp.route("/export", methods=["POST"])
@jwt_required()
def export_csv():
    """
    Trigger generation of user's parking history CSV.
    """
    from ..tasks import generate_user_csv
    
    uid = int(get_jwt_identity())
    task = generate_user_csv.delay(uid)
    return jsonify({"task_id": task.id}), 202


@bp.route("/export/<task_id>/status", methods=["GET"])
@jwt_required()
def export_status(task_id):
    """
    Check status of CSV export task.
    """
    from celery.result import AsyncResult
    from ..celery_app import celery
    
    result = AsyncResult(task_id, app=celery)
    
    response_data = {
        "task_id": task_id,
        "state": result.state,
    }
    
    if result.ready():
        if result.successful():
            response_data["result"] = result.result
            response_data["download_url"] = f"/user/export/{task_id}/download"
        else:
            response_data["error"] = str(result.result)
    else:
        response_data["result"] = None
        
    return jsonify(response_data), 200


@bp.route("/export/<task_id>/download", methods=["GET"])
@jwt_required()
def download_csv(task_id):
    """
    Download the generated CSV file.
    """
    from celery.result import AsyncResult
    from flask import send_file
    from ..celery_app import celery
    import os
    
    uid = int(get_jwt_identity())
    result = AsyncResult(task_id, app=celery)
    
    if not result.ready():
        return jsonify({"error": "Export not ready yet"}), 400
        
    if not result.successful():
        return jsonify({"error": "Export failed"}), 400
        
    file_path = result.result
    
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
        
    filename = os.path.basename(file_path)
    if f"user_{uid}_" not in filename:
        return jsonify({"error": "Unauthorized access"}), 403
    
    try:
        return send_file(
            file_path,
            as_attachment=True,
            download_name=f"parking_history_{uid}.csv",
            mimetype='text/csv'
        )
    except Exception as e:
        return jsonify({"error": f"Failed to send file: {str(e)}"}), 500


@bp.route("/export/cleanup", methods=["POST"])
@jwt_required()
def cleanup_exports():
    """
    Clean up old export files for the current user.
    """
    import os
    import glob
    from datetime import datetime, timedelta
    
    uid = int(get_jwt_identity())
    exports_dir = os.path.join(os.getcwd(), 'backend', 'exports')
    
    if not os.path.exists(exports_dir):
        return jsonify({"message": "No exports directory found"}), 200
    
    pattern = os.path.join(exports_dir, f"user_{uid}_reservations_*.csv")
    files_removed = 0
    cutoff_time = datetime.now() - timedelta(hours=24)
    
    for file_path in glob.glob(pattern):
        try:
            file_mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            if file_mtime < cutoff_time:
                os.remove(file_path)
                files_removed += 1
        except Exception as e:
            print(f"Failed to remove {file_path}: {e}")
    
    return jsonify({
        "message": f"Cleaned up {files_removed} old export files"
    }), 200