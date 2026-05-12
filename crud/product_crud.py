from typing import Any, Dict, List, Optional

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.product_schemas import ProductCreate, ProductUpdate


def get_products(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_products requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM products
        ORDER BY "productCode"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_products returned %s records", len(result))
    return result


def get_product_by_primary_key(db: Session, product_code: str) -> Dict[str, Any]:
    logger.info("get_product_by_primary_key requested for productCode=%s", product_code)
    query = text('SELECT * FROM products WHERE "productCode" = :product_code')
    row = db.execute(query, {"product_code": product_code}).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    result = dict(row)
    logger.info("get_product_by_primary_key returned record=%s", result)
    return result


def get_product_by_code(db: Session, product_code: str) -> Optional[Dict[str, Any]]:
    query = text('SELECT * FROM products WHERE "productCode" = :product_code')
    row = db.execute(query, {"product_code": product_code}).mappings().first()
    return dict(row) if row else None


def create_products(db: Session, product: ProductCreate) -> Dict[str, Any]:
    payload = product.model_dump()
    logger.info("create_products requested with payload=%s", payload)
    query = text(
        """
        INSERT INTO products (
            "productCode", "productName", "productLine", "productScale",
            "productVendor", "productDescription", "quantityInStock",
            "buyPrice", "MSRP"
        ) VALUES (
            :productCode, :productName, :productLine, :productScale,
            :productVendor, :productDescription, :quantityInStock,
            :buyPrice, :MSRP
        )
        RETURNING *
        """
    )
    try:
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_products returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_products integrity error: %s", exc)
        if "foreign key" in error_text and "productline" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid productLine. It must reference an existing productLine.",
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_products failed: %s", exc)
        raise


def create_product(db: Session, product: ProductCreate) -> Dict[str, Any]:
    return create_products(db, product)


def update_products(db: Session, product_code: str, product_update: ProductUpdate) -> Dict[str, Any]:
    values = product_update.model_dump(exclude_unset=True)
    logger.info("update_products requested for productCode=%s payload=%s", product_code, values)
    existing = get_product_by_primary_key(db, product_code)
    if not values:
        return existing

    set_clause = ", ".join([f'"{key}" = :{key}' for key in values.keys()])
    params = {"product_code": product_code, **values}

    query = text(
        f"""
        UPDATE products
        SET {set_clause}
        WHERE "productCode" = :product_code
        RETURNING *
        """
    )
    try:
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

        db.commit()
        result = dict(row)
        logger.info("update_products returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_products integrity error: %s", exc)
        if "foreign key" in error_text and "productline" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid productLine. It must reference an existing productLine.",
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_products failed: %s", exc)
        raise


def update_product(db: Session, product_code: str, product_update: ProductUpdate) -> Dict[str, Any]:
    return update_products(db, product_code, product_update)


def count_products(db: Session) -> int:
    logger.info("count_products requested")
    query = text('SELECT COUNT(*) as count FROM products')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_products returned %s", count)
    return count


def delete_products(db: Session, product_code: str) -> Dict[str, Any]:
    logger.info("delete_products requested for productCode=%s", product_code)
    existing = get_product_by_primary_key(db, product_code)
    query = text('DELETE FROM products WHERE "productCode" = :product_code')
    try:
        result = db.execute(query, {"product_code": product_code})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        db.commit()
        logger.info("delete_products returned deleted_record=%s", existing)
        return existing
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_products failed: %s", exc)
        raise


def delete_product(db: Session, product_code: str) -> Dict[str, Any]:
    return delete_products(db, product_code)


def get_product_orderdetails(db: Session, product_code: str) -> List[Dict[str, Any]]:
    logger.info("get_product_orderdetails requested for productCode=%s", product_code)
    query = text(
        """
        SELECT *
        FROM orderdetails
        WHERE "productCode" = :product_code
        ORDER BY "orderNumber"
        """
    )
    rows = db.execute(query, {"product_code": product_code}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_product_orderdetails returned %s records", len(result))
    return result
