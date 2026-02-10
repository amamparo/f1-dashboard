import sqlite3
from functools import lru_cache
from typing import Callable

import pandas as pd
from fastapi import Depends, Response, HTTPException, status
from pydantic import BaseModel

from esm_fullstack_challenge.db import DB, query_builder
from esm_fullstack_challenge.dependencies import get_db, CommonQueryParams
from esm_fullstack_challenge.models import AutoGenModels


@lru_cache()
def get_id_column_name(table: str) -> str | None:
    table_model = AutoGenModels[table]
    cols = table_model.model_fields.keys()
    for col in cols:
        if col == 'id' or col.endswith('_id'):
            return col
    return None


def get_route_list_function(table: str, table_model: BaseModel) -> Callable:
    """Generates an enpoint function to list all items.

    Args:
        table (str): Table name.
        table_model (BaseModel): Pydantic model for the table.

    Returns:
        Callable: Endpoint function.
    """
    def route_func_list_all(
            response: Response,
            cqp: CommonQueryParams = Depends(CommonQueryParams),
            db: DB = Depends(get_db)
    ):
        query_str = query_builder(
            table=table,
            order_by=cqp.order_by,
            limit=cqp.limit,
            offset=cqp.offset,
            filter_by=cqp.filter_by,
        )
        count_query_str = query_builder(
            table=table,
            filter_by=cqp.filter_by,
            count_only=True
        )

        with db.get_connection() as conn:
            df = pd.read_sql_query(query_str, conn)
            cur = conn.cursor()
            cur.execute(count_query_str)
            count = cur.fetchone()[0]

        data = [
            table_model(**item)
            for item in df.to_dict(orient='records')
        ]

        response.headers['Access-Control-Expose-Headers'] = 'Content-Range'
        response.headers['Content-Range'] = \
            f'{table} {cqp.offset}-{cqp.offset + len(data) - 1}/{count}'

        return data

    return route_func_list_all


def get_route_id_function(table: str, table_model: BaseModel) -> Callable:
    """Generates an enpoint function to get an item by ID.

    Args:
        table (str): Table name.
        table_model (BaseModel): Pydantic model for the table.

    Returns:
        Callable: Endpoint function.
    """
    def route_id_function(id: int, db: DB = Depends(get_db)):
        id_col = get_id_column_name(table)
        with db.get_connection() as conn:
            conn.row_factory = sqlite3.Row
            cur = conn.cursor()
            cur.execute(f'SELECT * FROM {table} WHERE {id_col} = {id};')
            item = cur.fetchone()
        if item:
            return table_model(**item)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f'Item with id={id} does not exist!'
            )

    return route_id_function
