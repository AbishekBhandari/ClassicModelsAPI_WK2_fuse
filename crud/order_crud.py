from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.order_schemas import OrderCreate, OrderUpdate


def get_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_orders requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM orders
        ORDER BY "orderNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_orders returned %s records", len(result))
    return result


def get_orders_by_customer(
    db: Session, customer_number: int, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    logger.info(
        "get_orders_by_customer requested with customerNumber=%s, skip=%s, limit=%s",
        customer_number,
        skip,
        limit,
    )
    query = text(
        """
        SELECT *
        FROM orders
        WHERE "customerNumber" = :customer_number
        ORDER BY "orderNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(
        query, {"customer_number": customer_number, "skip": skip, "limit": limit}
    ).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_orders_by_customer returned %s records", len(result))
    return result


def get_order_by_primary_key(db: Session, order_number: int) -> Dict[str, Any]:
    logger.info("get_order_by_primary_key requested for orderNumber=%s", order_number)
    query = text('SELECT * FROM orders WHERE "orderNumber" = :order_number')
    row = db.execute(query, {"order_number": order_number}).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    result = dict(row)
    logger.info("get_order_by_primary_key returned record=%s", result)
    return result


def create_orders(db: Session, order: OrderCreate) -> Dict[str, Any]:
    payload = order.model_dump()
    logger.info("create_orders requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO orders (
                "orderNumber", "orderDate", "requiredDate", "shippedDate",
                "status", "comments", "customerNumber"
            ) VALUES (
                :orderNumber, :orderDate, :requiredDate, :shippedDate,
                :status, :comments, :customerNumber
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_orders returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_orders integrity error: %s", exc)
        if "foreign key" in error_text and "customernumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid customerNumber. It must reference an existing customer.",
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_orders failed: %s", exc)
        raise


def update_orders(db: Session, order_number: int, order_update: OrderUpdate) -> Dict[str, Any]:
    payload = order_update.model_dump(exclude_unset=True)
    logger.info("update_orders requested for orderNumber=%s payload=%s", order_number, payload)
    existing = get_order_by_primary_key(db, order_number)
    if not payload:
        return existing
    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"order_number": order_number, **payload}
    try:
        query = text(
            f"""
            UPDATE orders
            SET {set_clause}
            WHERE "orderNumber" = :order_number
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        db.commit()
        result = dict(row)
        logger.info("update_orders returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_orders integrity error: %s", exc)
        if "foreign key" in error_text and "customernumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid customerNumber. It must reference an existing customer.",
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_orders failed: %s", exc)
        raise


def count_orders(db: Session) -> int:
    logger.info("count_orders requested")
    query = text('SELECT COUNT(*) as count FROM orders')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_orders returned %s", count)
    return count


def delete_orders(db: Session, order_number: int) -> Dict[str, Any]:
    logger.info("delete_orders requested for orderNumber=%s", order_number)
    existing = get_order_by_primary_key(db, order_number)
    try:
        query = text('DELETE FROM orders WHERE "orderNumber" = :order_number')
        result = db.execute(query, {"order_number": order_number})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        db.commit()
        logger.info("delete_orders returned deleted_record=%s", existing)
        return existing
    except IntegrityError as exc:
        db.rollback()
        logger.exception("delete_orders integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Order cannot be deleted because it still has related orderdetails.",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_orders failed: %s", exc)
        raise
