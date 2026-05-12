from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.customer_schemas import CustomerCreate, CustomerUpdate


def get_customers(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_customers requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM customers
        ORDER BY "customerNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_customers returned %s records", len(result))
    return result


def get_customer_by_primary_key(db: Session, customer_number: int) -> Dict[str, Any]:
    logger.info("get_customer_by_primary_key requested for customerNumber=%s", customer_number)
    query = text('SELECT * FROM customers WHERE "customerNumber" = :customer_number')
    row = db.execute(query, {"customer_number": customer_number}).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    result = dict(row)
    logger.info("get_customer_by_primary_key returned record=%s", result)
    return result


def create_customers(db: Session, customer: CustomerCreate) -> Dict[str, Any]:
    payload = customer.model_dump()
    logger.info("create_customers requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO customers (
                "customerNumber", "customerName", "contactLastName", "contactFirstName",
                "phone", "addressLine1", "addressLine2", "city", "state",
                "postalCode", "country", "salesRepEmployeeNumber", "creditLimit"
            ) VALUES (
                :customerNumber, :customerName, :contactLastName, :contactFirstName,
                :phone, :addressLine1, :addressLine2, :city, :state,
                :postalCode, :country, :salesRepEmployeeNumber, :creditLimit
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_customers returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_customers integrity error: %s", exc)
        if "foreign key" in error_text and "salesrepemployeenumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid salesRepEmployeeNumber. It must reference an existing employee.",
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_customers failed: %s", exc)
        raise


def update_customers(
    db: Session, customer_number: int, customer_update: CustomerUpdate
) -> Dict[str, Any]:
    payload = customer_update.model_dump(exclude_unset=True)
    logger.info(
        "update_customers requested for customerNumber=%s payload=%s",
        customer_number,
        payload,
    )
    existing = get_customer_by_primary_key(db, customer_number)
    if not payload:
        return existing
    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"customer_number": customer_number, **payload}
    try:
        query = text(
            f"""
            UPDATE customers
            SET {set_clause}
            WHERE "customerNumber" = :customer_number
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        db.commit()
        result = dict(row)
        logger.info("update_customers returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_customers integrity error: %s", exc)
        if "foreign key" in error_text and "salesrepemployeenumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid salesRepEmployeeNumber. It must reference an existing employee.",
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_customers failed: %s", exc)
        raise


def count_customers(db: Session) -> int:
    logger.info("count_customers requested")
    query = text('SELECT COUNT(*) as count FROM customers')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_customers returned %s", count)
    return count


def delete_customers(db: Session, customer_number: int) -> Dict[str, Any]:
    logger.info("delete_customers requested for customerNumber=%s", customer_number)
    existing = get_customer_by_primary_key(db, customer_number)
    try:
        query = text('DELETE FROM customers WHERE "customerNumber" = :customer_number')
        result = db.execute(query, {"customer_number": customer_number})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
        db.commit()
        logger.info("delete_customers returned deleted_record=%s", existing)
        return existing
    except IntegrityError as exc:
        db.rollback()
        logger.exception("delete_customers integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Customer cannot be deleted because it is referenced by other records.",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_customers failed: %s", exc)
        raise
