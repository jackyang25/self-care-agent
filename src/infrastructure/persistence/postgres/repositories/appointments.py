"""appointment data access functions."""

from typing import Optional, List, Dict, Any
from src.infrastructure.persistence.postgres.connection import get_db_cursor


def create_appointment(
    appointment_id: str,
    user_id: str,
    provider_id: Optional[str],
    specialty: str,
    appointment_date: str,
    appointment_time: str,
    status: str = "scheduled",
    reason: Optional[str] = None,
    sync_status: str = "pending",
) -> bool:
    """create a new appointment.

    args:
        appointment_id: unique appointment id
        user_id: user uuid
        provider_id: provider uuid (can be None)
        specialty: medical specialty
        appointment_date: date in YYYY-MM-DD format
        appointment_time: time in HH:MM:SS format
        status: appointment status (default: 'scheduled')
        reason: reason for appointment
        sync_status: sync status (default: 'pending')

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                INSERT INTO appointments (
                    appointment_id, user_id, provider_id, specialty,
                    appointment_date, appointment_time, status, reason,
                    sync_status, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, now()
                )
                """,
                (
                    appointment_id,
                    user_id,
                    provider_id,
                    specialty,
                    appointment_date,
                    appointment_time,
                    status,
                    reason,
                    sync_status,
                ),
            )
            return True
    except Exception:
        return False


def get_user_appointments(user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """get appointments for a user.

    args:
        user_id: user uuid
        limit: maximum number of results

    returns:
        list of appointment dicts with provider details
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    a.appointment_id,
                    a.user_id,
                    a.provider_id,
                    a.specialty,
                    a.appointment_date,
                    a.appointment_time,
                    a.status,
                    a.reason,
                    a.sync_status,
                    a.created_at,
                    p.name as provider_name,
                    p.facility as provider_facility,
                    p.contact_info as provider_contact
                FROM appointments a
                LEFT JOIN providers p ON a.provider_id = p.provider_id
                WHERE a.user_id = %s
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
                LIMIT %s
                """,
                (user_id, limit),
            )
            results = cur.fetchall()
            return [dict(row) for row in results]
    except Exception:
        return []


def get_appointment_by_id(appointment_id: str) -> Optional[Dict[str, Any]]:
    """get appointment by appointment_id.

    args:
        appointment_id: appointment id

    returns:
        appointment dict with provider details, or None if not found
    """
    try:
        with get_db_cursor() as cur:
            cur.execute(
                """
                SELECT 
                    a.appointment_id,
                    a.user_id,
                    a.provider_id,
                    a.specialty,
                    a.appointment_date,
                    a.appointment_time,
                    a.status,
                    a.reason,
                    a.sync_status,
                    a.created_at,
                    p.name as provider_name,
                    p.facility as provider_facility,
                    p.contact_info as provider_contact
                FROM appointments a
                LEFT JOIN providers p ON a.provider_id = p.provider_id
                WHERE a.appointment_id = %s
                """,
                (appointment_id,),
            )
            result = cur.fetchone()
            return dict(result) if result else None
    except Exception:
        return None


def update_appointment_status(
    appointment_id: str,
    status: str,
    sync_status: Optional[str] = None,
) -> bool:
    """update appointment status.

    args:
        appointment_id: appointment id
        status: new status (e.g., 'confirmed', 'cancelled', 'completed')
        sync_status: optional sync status update

    returns:
        True if successful, False otherwise
    """
    try:
        with get_db_cursor() as cur:
            if sync_status:
                cur.execute(
                    """
                    UPDATE appointments
                    SET status = %s, sync_status = %s
                    WHERE appointment_id = %s
                    """,
                    (status, sync_status, appointment_id),
                )
            else:
                cur.execute(
                    """
                    UPDATE appointments
                    SET status = %s
                    WHERE appointment_id = %s
                    """,
                    (status, appointment_id),
                )
            return cur.rowcount > 0
    except Exception:
        return False

