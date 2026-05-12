from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.orderdetail_schemas import OrderDetailCreate, OrderDetailUpdate


def get_orderdetails(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_orderdetails requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM orderdetails
        ORDER BY "orderNumber", "productCode"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_orderdetails returned %s records", len(result))
    return result


def get_orderdetail_by_primary_key(
    db: Session, order_number: int, product_code: str
) -> Dict[str, Any]:
    logger.info(
        "get_orderdetail_by_primary_key requested for orderNumber=%s, productCode=%s",
        order_number,
        product_code,
    )
    query = text(
        """
        SELECT *
        FROM orderdetails
        WHERE "orderNumber" = :order_number
          AND "productCode" = :product_code
        """
    )
    row = db.execute(
        query,
        {"order_number": order_number, "product_code": product_code},
    ).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrderDetail not found")
    result = dict(row)
    logger.info("get_orderdetail_by_primary_key returned record=%s", result)
    return result


def get_orderdetail(db: Session, order_number: int, product_code: str) -> Dict[str, Any]:
    return get_orderdetail_by_primary_key(db, order_number, product_code)


def create_orderdetails(db: Session, orderdetail: OrderDetailCreate) -> Dict[str, Any]:
    payload = orderdetail.model_dump()
    logger.info("create_orderdetails requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO orderdetails (
                "orderNumber", "productCode", "quantityOrdered", "priceEach", "orderLineNumber"
            ) VALUES (
                :orderNumber, :productCode, :quantityOrdered, :priceEach, :orderLineNumber
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_orderdetails returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_orderdetails integrity error: %s", exc)
        if "foreign key" in error_text and "ordernumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid orderNumber. It must reference an existing order.",
            ) from exc
        if "foreign key" in error_text and "productcode" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid productCode. It must reference an existing product.",
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_orderdetails failed: %s", exc)
        raise


def update_orderdetails(
    db: Session, order_number: int, product_code: str, orderdetail_update: OrderDetailUpdate
) -> Dict[str, Any]:
    payload = orderdetail_update.model_dump(exclude_unset=True)
    logger.info(
        "update_orderdetails requested for orderNumber=%s, productCode=%s payload=%s",
        order_number,
        product_code,
        payload,
    )
    existing = get_orderdetail_by_primary_key(db, order_number, product_code)
    if not payload:
        return existing
    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"order_number": order_number, "product_code": product_code, **payload}
    try:
        query = text(
            f"""
            UPDATE orderdetails
            SET {set_clause}
            WHERE "orderNumber" = :order_number
              AND "productCode" = :product_code
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrderDetail not found")
        db.commit()
        result = dict(row)
        logger.info("update_orderdetails returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_orderdetails integrity error: %s", exc)
        if "foreign key" in error_text and "ordernumber" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid orderNumber. It must reference an existing order.",
            ) from exc
        if "foreign key" in error_text and "productcode" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid productCode. It must reference an existing product.",
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_orderdetails failed: %s", exc)
        raise


def count_orderdetails(db: Session) -> int:
    logger.info("count_orderdetails requested")
    query = text('SELECT COUNT(*) as count FROM orderdetails')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_orderdetails returned %s", count)
    return count


def delete_orderdetails(db: Session, order_number: int, product_code: str) -> Dict[str, Any]:
    logger.info(
        "delete_orderdetails requested for orderNumber=%s, productCode=%s",
        order_number,
        product_code,
    )
    existing = get_orderdetail_by_primary_key(db, order_number, product_code)
    try:
        query = text(
            """
            DELETE FROM orderdetails
            WHERE "orderNumber" = :order_number
              AND "productCode" = :product_code
            """
        )
        result = db.execute(query, {"order_number": order_number, "product_code": product_code})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="OrderDetail not found")
        db.commit()
        logger.info("delete_orderdetails returned deleted_record=%s", existing)
        return existing
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_orderdetails failed: %s", exc)
        raise
