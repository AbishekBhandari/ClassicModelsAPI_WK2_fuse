from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.payment_schemas import PaymentCreate, PaymentUpdate


def get_payments(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_payments requested with skip=%s, limit=%s", skip, limit)
    try:
        query = text(
            """
            SELECT *
            FROM payments
            ORDER BY "customerNumber", "checkNumber"
            OFFSET :skip
            LIMIT :limit
            """
        )
        rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
        result = [dict(row) for row in rows]
        logger.info("get_payments returned %s records", len(result))
        return result
    except Exception as exc:
        logger.exception("get_payments failed: %s", exc)
        raise


def get_payments_by_customer(
    db: Session, customer_number: int, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    logger.info(
        "get_payments_by_customer requested with customerNumber=%s, skip=%s, limit=%s",
        customer_number,
        skip,
        limit,
    )
    try:
        query = text(
            """
            SELECT *
            FROM payments
            WHERE "customerNumber" = :customer_number
            ORDER BY "checkNumber"
            OFFSET :skip
            LIMIT :limit
            """
        )
        rows = db.execute(
            query,
            {"customer_number": customer_number, "skip": skip, "limit": limit},
        ).mappings().all()
        result = [dict(row) for row in rows]
        logger.info("get_payments_by_customer returned %s records", len(result))
        return result
    except Exception as exc:
        logger.exception("get_payments_by_customer failed: %s", exc)
        raise


def get_payment_by_primary_key(
    db: Session, customer_number: int, check_number: str
) -> Dict[str, Any]:
    logger.info(
        "get_payment_by_primary_key requested with customerNumber=%s, checkNumber=%s",
        customer_number,
        check_number,
    )
    try:
        query = text(
            """
            SELECT *
            FROM payments
            WHERE "customerNumber" = :customer_number
              AND "checkNumber" = :check_number
            """
        )
        row = db.execute(
            query,
            {"customer_number": customer_number, "check_number": check_number},
        ).mappings().first()

        if not row:
            logger.warning(
                "Payment not found for customerNumber=%s, checkNumber=%s",
                customer_number,
                check_number,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )

        result = dict(row)
        logger.info("get_payment_by_primary_key returned record=%s", result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("get_payment_by_primary_key failed: %s", exc)
        raise


def create_payments(db: Session, payment: PaymentCreate) -> Dict[str, Any]:
    payload = payment.model_dump()
    logger.info("create_payments requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO payments (
                "customerNumber", "checkNumber", "paymentDate", "amount"
            ) VALUES (
                :customerNumber, :checkNumber, :paymentDate, :amount
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_payments returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_payments integrity error: %s", exc)
        if "foreign key" in error_text and "customernumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid customerNumber '{payment.customerNumber}'. "
                    "It must reference an existing customers.customerNumber."
                ),
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_payments failed: %s", exc)
        raise


def update_payments(
    db: Session,
    customer_number: int,
    check_number: str,
    payment_update: PaymentUpdate,
) -> Dict[str, Any]:
    payload = payment_update.model_dump(exclude_unset=True)
    logger.info(
        "update_payments requested for customerNumber=%s, checkNumber=%s with payload=%s",
        customer_number,
        check_number,
        payload,
    )

    existing = get_payment_by_primary_key(db, customer_number, check_number)
    if not payload:
        logger.info("update_payments no changes provided, returned existing record=%s", existing)
        return existing

    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {
        "customer_number": customer_number,
        "check_number": check_number,
        **payload,
    }

    try:
        query = text(
            f"""
            UPDATE payments
            SET {set_clause}
            WHERE "customerNumber" = :customer_number
              AND "checkNumber" = :check_number
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            logger.warning(
                "Payment not found during update for customerNumber=%s, checkNumber=%s",
                customer_number,
                check_number,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        db.commit()
        result = dict(row)
        logger.info("update_payments returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_payments integrity error: %s", exc)
        if "foreign key" in error_text and "customernumber" in error_text:
            invalid_value = payload.get("customerNumber")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=(
                    f"Invalid customerNumber '{invalid_value}'. "
                    "It must reference an existing customers.customerNumber."
                ),
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_payments failed: %s", exc)
        raise


def count_payments(db: Session) -> int:
    logger.info("count_payments requested")
    query = text('SELECT COUNT(*) as count FROM payments')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_payments returned %s", count)
    return count


def delete_payments(db: Session, customer_number: int, check_number: str) -> Dict[str, Any]:
    logger.info(
        "delete_payments requested for customerNumber=%s, checkNumber=%s",
        customer_number,
        check_number,
    )
    existing = get_payment_by_primary_key(db, customer_number, check_number)
    try:
        query = text(
            """
            DELETE FROM payments
            WHERE "customerNumber" = :customer_number
              AND "checkNumber" = :check_number
            """
        )
        result = db.execute(
            query,
            {"customer_number": customer_number, "check_number": check_number},
        )
        if result.rowcount == 0:
            db.rollback()
            logger.warning(
                "Payment not found during delete for customerNumber=%s, checkNumber=%s",
                customer_number,
                check_number,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found",
            )
        db.commit()
        logger.info("delete_payments returned deleted_record=%s", existing)
        return existing
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_payments failed: %s", exc)
        raise
