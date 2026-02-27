from typing import List

import pandas as pd
from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from esm_fullstack_challenge.db import DB, query_builder
from esm_fullstack_challenge.dependencies import get_db, CommonQueryParams
from esm_fullstack_challenge.models import AutoGenModels
from esm_fullstack_challenge.routers.utils import (
    get_route_list_function,
    get_route_id_function,
)


predictions_router = APIRouter()
table_model = AutoGenModels['predictions']


# Standard list/detail endpoints (React-Admin compatible)
get_predictions = get_route_list_function('predictions', table_model)
predictions_router.add_api_route(
    '', get_predictions,
    methods=["GET"], response_model=List[table_model],
)

get_prediction = get_route_id_function('predictions', table_model)
predictions_router.add_api_route(
    '/{id}', get_prediction,
    methods=["GET"], response_model=table_model,
)


class PredictionCreate(BaseModel):
    race_id: int
    driver_id: int
    constructor_id: int | None = None
    grid: int | None = None
    predicted_position: int
    actual_position: int | None = None
    predicted_delta: int | None = None
    actual_delta: int | None = None
    confidence: float | None = None
    model_version: str


class PredictionBatchCreate(BaseModel):
    predictions: List[PredictionCreate]


@predictions_router.post('')
def create_predictions(
    batch: PredictionBatchCreate,
    db: DB = Depends(get_db),
):
    """Batch-insert predictions for a race."""
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for p in batch.predictions:
            cursor.execute(
                """INSERT INTO predictions
                   (race_id, driver_id, constructor_id, grid,
                    predicted_position, actual_position,
                    predicted_delta, actual_delta,
                    confidence, model_version)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (p.race_id, p.driver_id, p.constructor_id, p.grid,
                 p.predicted_position, p.actual_position,
                 p.predicted_delta, p.actual_delta,
                 p.confidence, p.model_version),
            )
    return {"status": "ok", "count": len(batch.predictions)}


@predictions_router.get('/enriched')
def get_enriched_predictions(
    response: Response,
    cqp: CommonQueryParams = Depends(CommonQueryParams),
    db: DB = Depends(get_db),
):
    """Get predictions joined with driver names, race info, and constructor names."""
    base_query = (
        "SELECT"
        "    p.id,"
        "    p.race_id,"
        "    p.driver_id,"
        "    d.forename || ' ' || d.surname AS driver_name,"
        "    d.code AS driver_code,"
        "    c.name AS constructor_name,"
        "    r.name AS race_name,"
        "    r.year,"
        "    r.round,"
        "    p.grid,"
        "    p.predicted_position,"
        "    p.actual_position,"
        "    p.predicted_delta,"
        "    p.actual_delta,"
        "    p.confidence,"
        "    p.model_version,"
        "    p.created_at"
        " FROM predictions p"
        " JOIN drivers d ON p.driver_id = d.id"
        " JOIN races r ON p.race_id = r.id"
        " LEFT JOIN constructors c ON p.constructor_id = c.id"
    )
    query_str = query_builder(
        custom_select=base_query,
        order_by=cqp.order_by or [('p.id', 'desc')],
        limit=cqp.limit,
        offset=cqp.offset,
        filter_by=cqp.filter_by,
    )
    with db.get_connection() as conn:
        df = pd.read_sql_query(query_str, conn)
    return df.to_dict(orient='records')


@predictions_router.get('/model-input/{race_id}')
def get_model_input(race_id: int, db: DB = Depends(get_db)):
    """Get feature data for the prediction model for a specific race."""
    query = """
        SELECT
            r.race_id,
            r.driver_id,
            r.constructor_id,
            r.grid,
            r.position_order AS actual_position,
            d.forename || ' ' || d.surname AS driver_name,
            c.name AS constructor_name,
            ds.points AS championship_points,
            ds.position AS championship_position,
            ds.wins AS season_wins,
            ci.lat AS circuit_lat,
            ci.lng AS circuit_lng,
            ci.alt AS circuit_altitude,
            ci.country AS circuit_country,
            races.year,
            races.round
        FROM results r
        JOIN drivers d ON r.driver_id = d.id
        JOIN constructors c ON r.constructor_id = c.id
        JOIN races ON r.race_id = races.id
        JOIN circuits ci ON races.circuit_id = ci.id
        LEFT JOIN driver_standings ds ON (
            ds.driver_id = r.driver_id
            AND ds.race_id = (
                SELECT MAX(r2.id) FROM races r2
                WHERE r2.year = races.year AND r2.round < races.round
            )
        )
        WHERE r.race_id = ?
        ORDER BY r.grid ASC
    """
    with db.get_connection() as conn:
        df = pd.read_sql_query(query, conn, params=[race_id])
    records = df.to_dict(orient='records')
    for row in records:
        for k, v in row.items():
            if pd.isna(v):
                row[k] = None
    return records
