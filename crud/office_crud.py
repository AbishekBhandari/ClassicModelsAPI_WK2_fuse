from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.office_schemas import OfficeCreate, OfficeUpdate


def get_offices(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_offices requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM offices
        ORDER BY "officeCode"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_offices returned %s records", len(result))
    return result


def get_office_by_primary_key(db: Session, office_code: str) -> Dict[str, Any]:
    logger.info("get_office_by_primary_key requested for officeCode=%s", office_code)
    query = text('SELECT * FROM offices WHERE "officeCode" = :office_code')
    row = db.execute(query, {"office_code": office_code}).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")
    result = dict(row)
    logger.info("get_office_by_primary_key returned record=%s", result)
    return result


def get_office_employees(
    db: Session, office_code: str, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    logger.info(
        "get_office_employees requested with officeCode=%s, skip=%s, limit=%s",
        office_code,
        skip,
        limit,
    )
    query = text(
        """
        SELECT *
        FROM employees
        WHERE "officeCode" = :office_code
        ORDER BY "employeeNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(
        query, {"office_code": office_code, "skip": skip, "limit": limit}
    ).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_office_employees returned %s records", len(result))
    return result


def create_offices(db: Session, office: OfficeCreate) -> Dict[str, Any]:
    payload = office.model_dump()
    logger.info("create_offices requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO offices (
                "officeCode", "city", "phone", "addressLine1", "addressLine2",
                "state", "country", "postalCode", "territory"
            ) VALUES (
                :officeCode, :city, :phone, :addressLine1, :addressLine2,
                :state, :country, :postalCode, :territory
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_offices returned record=%s", result)
        return result
    except Exception as exc:
        db.rollback()
        logger.exception("create_offices failed: %s", exc)
        raise


def update_offices(db: Session, office_code: str, office_update: OfficeUpdate) -> Dict[str, Any]:
    payload = office_update.model_dump(exclude_unset=True)
    logger.info("update_offices requested for officeCode=%s payload=%s", office_code, payload)
    existing = get_office_by_primary_key(db, office_code)
    if not payload:
        return existing
    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"office_code": office_code, **payload}
    try:
        query = text(
            f"""
            UPDATE offices
            SET {set_clause}
            WHERE "officeCode" = :office_code
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")
        db.commit()
        result = dict(row)
        logger.info("update_offices returned record=%s", result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_offices failed: %s", exc)
        raise


def count_offices(db: Session) -> int:
    logger.info("count_offices requested")
    query = text('SELECT COUNT(*) as count FROM offices')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_offices returned %s", count)
    return count


def delete_offices(db: Session, office_code: str) -> Dict[str, Any]:
    logger.info("delete_offices requested for officeCode=%s", office_code)
    existing = get_office_by_primary_key(db, office_code)
    try:
        query = text('DELETE FROM offices WHERE "officeCode" = :office_code')
        result = db.execute(query, {"office_code": office_code})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Office not found")
        db.commit()
        logger.info("delete_offices returned deleted_record=%s", existing)
        return existing
    except IntegrityError as exc:
        db.rollback()
        logger.exception("delete_offices integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Office cannot be deleted because it still has assigned employees.",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_offices failed: %s", exc)
        raise
