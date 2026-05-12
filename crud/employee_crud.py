from typing import Any, Dict, List

from fastapi import HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from logger import logger
from schemas.employee_schemas import EmployeeCreate, EmployeeUpdate


def get_employees(db: Session, skip: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
    logger.info("get_employees requested with skip=%s, limit=%s", skip, limit)
    query = text(
        """
        SELECT *
        FROM employees
        ORDER BY "employeeNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(query, {"skip": skip, "limit": limit}).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_employees returned %s records", len(result))
    return result


def get_employee_by_primary_key(db: Session, employee_number: int) -> Dict[str, Any]:
    logger.info("get_employee_by_primary_key requested for employeeNumber=%s", employee_number)
    query = text('SELECT * FROM employees WHERE "employeeNumber" = :employee_number')
    row = db.execute(query, {"employee_number": employee_number}).mappings().first()
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
    result = dict(row)
    logger.info("get_employee_by_primary_key returned record=%s", result)
    return result


def get_employee_reports(
    db: Session, employee_number: int, skip: int = 0, limit: int = 100
) -> List[Dict[str, Any]]:
    logger.info(
        "get_employee_reports requested with employeeNumber=%s, skip=%s, limit=%s",
        employee_number,
        skip,
        limit,
    )
    query = text(
        """
        SELECT *
        FROM employees
        WHERE "reportsTo" = :employee_number
        ORDER BY "employeeNumber"
        OFFSET :skip
        LIMIT :limit
        """
    )
    rows = db.execute(
        query, {"employee_number": employee_number, "skip": skip, "limit": limit}
    ).mappings().all()
    result = [dict(row) for row in rows]
    logger.info("get_employee_reports returned %s records", len(result))
    return result


def create_employees(db: Session, employee: EmployeeCreate) -> Dict[str, Any]:
    payload = employee.model_dump()
    logger.info("create_employees requested with payload=%s", payload)
    try:
        query = text(
            """
            INSERT INTO employees (
                "employeeNumber", "lastName", "firstName", "extension", "email",
                "officeCode", "reportsTo", "jobTitle"
            ) VALUES (
                :employeeNumber, :lastName, :firstName, :extension, :email,
                :officeCode, :reportsTo, :jobTitle
            )
            RETURNING *
            """
        )
        row = db.execute(query, payload).mappings().one()
        db.commit()
        result = dict(row)
        logger.info("create_employees returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("create_employees integrity error: %s", exc)
        if "foreign key" in error_text and "officecode" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid officeCode. It must reference an existing office.",
            ) from exc
        if "foreign key" in error_text and "reportsto" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid reportsTo. It must reference an existing employeeNumber.",
            ) from exc
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("create_employees failed: %s", exc)
        raise


def update_employees(
    db: Session, employee_number: int, employee_update: EmployeeUpdate
) -> Dict[str, Any]:
    payload = employee_update.model_dump(exclude_unset=True)
    logger.info(
        "update_employees requested for employeeNumber=%s payload=%s",
        employee_number,
        payload,
    )
    existing = get_employee_by_primary_key(db, employee_number)
    if not payload:
        return existing
    set_clause = ", ".join([f'"{key}" = :{key}' for key in payload.keys()])
    params = {"employee_number": employee_number, **payload}
    try:
        query = text(
            f"""
            UPDATE employees
            SET {set_clause}
            WHERE "employeeNumber" = :employee_number
            RETURNING *
            """
        )
        row = db.execute(query, params).mappings().first()
        if not row:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        db.commit()
        result = dict(row)
        logger.info("update_employees returned record=%s", result)
        return result
    except IntegrityError as exc:
        db.rollback()
        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()
        logger.exception("update_employees integrity error: %s", exc)
        if "foreign key" in error_text and "officecode" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid officeCode. It must reference an existing office.",
            ) from exc
        if "foreign key" in error_text and "reportsto" in error_text:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Invalid reportsTo. It must reference an existing employeeNumber.",
            ) from exc
        raise
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("update_employees failed: %s", exc)
        raise


def count_employees(db: Session) -> int:
    logger.info("count_employees requested")
    query = text('SELECT COUNT(*) as count FROM employees')
    result = db.execute(query).mappings().first()
    count = result['count'] if result else 0
    logger.info("count_employees returned %s", count)
    return count


def delete_employees(db: Session, employee_number: int) -> Dict[str, Any]:
    logger.info("delete_employees requested for employeeNumber=%s", employee_number)
    existing = get_employee_by_primary_key(db, employee_number)
    try:
        query = text('DELETE FROM employees WHERE "employeeNumber" = :employee_number')
        result = db.execute(query, {"employee_number": employee_number})
        if result.rowcount == 0:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Employee not found")
        db.commit()
        logger.info("delete_employees returned deleted_record=%s", existing)
        return existing
    except IntegrityError as exc:
        db.rollback()
        logger.exception("delete_employees integrity error: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                "Employee cannot be deleted because they have direct reports "
                "or are assigned as a sales representative for customers."
            ),
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:
        db.rollback()
        logger.exception("delete_employees failed: %s", exc)
        raise
