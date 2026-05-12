import asyncio
import time

from fastapi import FastAPI
from routers import (
    customer_router,
    product_router,
    productline_router,
    office_router,
    employee_router,
    order_router,
    orderdetail_router,
    payment_router,
)
from crud.customer_crud import count_customers
from crud.order_crud import count_orders
from crud.product_crud import count_products
from crud.employee_crud import count_employees
from crud.office_crud import count_offices
from crud.payment_crud import count_payments
from crud.orderdetail_crud import count_orderdetails
from crud.productline_crud import count_productlines
from database import engine, Base, SessionLocal
from logger import get_logger

logger = get_logger(__name__)
app = FastAPI(title='ClassicModels API', version='2.0')
app.include_router(customer_router.router, prefix='/customers', tags=['customers'])
app.include_router(product_router.router, prefix='/products', tags=['products'])
app.include_router(productline_router.router, prefix='/productlines', tags=['productlines'])
app.include_router(office_router.router, prefix='/offices', tags=['offices'])
app.include_router(employee_router.router, prefix='/employees', tags=['employees'])
app.include_router(order_router.router, prefix='/orders', tags=['orders'])
app.include_router(orderdetail_router.router, prefix='/orderdetails', tags=['orderdetails'])
app.include_router(payment_router.router, prefix='/payments', tags=['payments'])


def _count_in_executor(count_fn):
    db = SessionLocal()
    try:
        return count_fn(db)
    finally:
        db.close()


@app.get('/overall_counts')
async def overall_counts():
    logger.info('Starting overall_counts tasks')
    start_time = time.monotonic()
    loop = asyncio.get_running_loop()
    tasks = [
        loop.run_in_executor(None, _count_in_executor, count_customers),
        loop.run_in_executor(None, _count_in_executor, count_orders),
        loop.run_in_executor(None, _count_in_executor, count_products),
        loop.run_in_executor(None, _count_in_executor, count_employees),
        loop.run_in_executor(None, _count_in_executor, count_offices),
        loop.run_in_executor(None, _count_in_executor, count_payments),
        loop.run_in_executor(None, _count_in_executor, count_orderdetails),
        loop.run_in_executor(None, _count_in_executor, count_productlines),
    ]

    customers, orders, products, employees, offices, payments, orderdetails, productlines = await asyncio.gather(*tasks)
    elapsed = time.monotonic() - start_time
    logger.info('overall_counts completed in %.3f seconds', elapsed)

    return {
        'customers': customers,
        'orders': orders,
        'products': products,
        'employees': employees,
        'offices': offices,
        'payments': payments,
        'orderdetails': orderdetails,
        'productlines': productlines,
    }


@app.get('/')
def root():
    logger.info('Root endpoint accessed')
    return {'message': 'ClassicModels API is running!'}