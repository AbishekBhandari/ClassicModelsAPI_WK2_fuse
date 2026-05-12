from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.productline_schemas import ProductLineCreate, ProductLineUpdate


def get_productlines(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_productlines requested with skip=%s, limit=%s", skip, limit)
    try:
        query = text(
            """
            SELECT *
            FROM productlines
            ORDER BY "productLine"
            OFFSET :skip
            LIMIT :limit
            """
        )
        rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
        result = [dict(row) for row in rows]
        logger.info("get_productlines returned %s records", len(result))
        return result
    except Exception as exc:
        logger.exception("get_productlines failed: %s", exc)
        raise


def get_productline_by_primary_key(db: Session, product_line: str) -> Dict[str, Any]:
    logger.info("get_productline_by_primary_key requested for productLine=%s", product_line)
    query = text('SELECT * FROM productlines WHERE "productLine" = :product_line')
    row = db.execute(query, {"product_line": product_line}).mappings().first()
    if not row:
        logger.warning("ProductLine not found for productLine=%s", product_line)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductLine not found")
    result = dict(row)
    logger.info("get_productline_by_primary_key returned record=%s", result)
    return result


def create_productlines(db: Session, product_line: ProductLineCreate) -> Dict[str, Any]:
    payload = product_line.model_dump()
    logger.info("create_productlines requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO productlines ("productLine", "textDescription", "htmlDescription", "image")
            VALUES (:productLine, :textDescription, :htmlDescription, :image)
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_productlines returned record=%s", result)
        return result
    except Exception as exc:
        db.rollback()
        logger.exception("create_productlines failed: %s", exc)
        raise


def update_productlines(
    db: Session, product_line: str, product_line_update: ProductLineUpdate
) -> Dict[str, Any]:
    payload = product_line_update.model_dump(exclude_unset=True)
    logger.info(
        "update_productlines requested for productLine=%s with payload=%s",
        product_line,
        payload,
    )
    existing = get_productline_by_primary_key(db, product_line)
    if not payload:
        logger.info("update_productlines no changes, returned existing record=%s", existing)
        return existing

    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"product_line": product_line, **payload}
    try:
        query = text(
            f"""
            UPDATE productlines
            SET {set_clause}
            WHERE "productLine" = :product_line
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductLine not found")
        db.commit()
        result = dict(row)
        logger.info("update_productlines returned record=%s", result)
        return result
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_productlines failed: %s", exc)
        raise


def count_productlines(db: Session) -> int:
    logger.info("count_productlines requested")
    query = text('SELECT COUNT(*) as count FROM productlines')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_productlines returned %s", count)
    return count


def delete_productlines(db: Session, product_line: str) -> Dict[str, Any]:
    logger.info("delete_productlines requested for productLine=%s", product_line)
    existing = get_productline_by_primary_key(db, product_line)
    try:
        query = text('DELETE FROM productlines WHERE "productLine" = :product_line')
        result = db.execute(query, {"product_line": product_line})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ProductLine not found")
        db.commit()
        logger.info("delete_productlines returned deleted_record=%s", existing)
        return existing
    except IntegrityError as exc:
        db.rollback()
        logger.exception("delete_productlines integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="ProductLine cannot be deleted because products still reference it.",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_productlines failed: %s", exc)
        raise
