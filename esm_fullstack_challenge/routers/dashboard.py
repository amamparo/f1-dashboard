from typing import Optional

import pandas as pd
from fastapi import APIRouter, Depends, Query

from esm_fullstack_challenge.db import DB, query_builder
from esm_fullstack_challenge.dependencies import get_db, CommonQueryParams


dashboard_router = APIRouter()


@dashboard_router.get("/top_drivers_by_wins")
def get_top_drivers_by_wins(
    cqp: CommonQueryParams = Depends(CommonQueryParams),
    db: DB = Depends(get_db)
) -> list:
    """Gets top drivers by wins.

    Args:
        cqp (CommonQueryParams, optional): Common query params used for filtering.
                                           Defaults to Depends(CommonQueryParams).
        db (DB, optional): SQLite DB connection. Defaults to Depends(get_db).

    Returns:
        list: list of top drivers by wins.
    """
    base_query_str = (
        "with driver_wins as (\n"
        "    select d.id,\n"
        "        d.forename || ' ' || d.surname as full_name,\n"
        "        d.nationality,\n"
        "        d.dob,\n"
        "        date() - date(dob)             as age,\n"
        "        d.url\n"
        "    from drivers d\n"
        "          join results r on d.id = r.driver_id\n"
        "          join status s on r.status_id = s.id\n"
        "    where s.status = 'Finished'\n"
        "    and r.position_order = 1\n"
        ")\n"
        "select\n"
        "    *,\n"
        "    count(*) as number_of_wins\n"
        "from driver_wins"
    )
    query_str = query_builder(
        custom_select=base_query_str,
        order_by=cqp.order_by or [('number_of_wins', 'desc')],
        limit=cqp.limit,
        offset=cqp.offset,
        filter_by=cqp.filter_by,
        group_by=['id', 'full_name', 'nationality', 'dob', 'age', 'url']
    )
    with db.get_connection() as conn:
        df = pd.read_sql_query(query_str, conn)
        drivers = list(df.to_dict(orient='records'))

    return drivers


@dashboard_router.get("/championship_progression")
def get_championship_progression(
    season: Optional[int] = Query(None),
    db: DB = Depends(get_db),
) -> list:
    """Get championship points progression by round for a season."""
    with db.get_connection() as conn:
        if season is None:
            row = conn.execute(
                "SELECT MAX(year) FROM races"
            ).fetchone()
            season = row[0]

        df = pd.read_sql_query(
            "SELECT r.round, r.name AS race_name,"
            "       d.forename || ' ' || d.surname AS driver_name,"
            "       ds.points"
            " FROM driver_standings ds"
            " JOIN races r ON ds.race_id = r.id"
            " JOIN drivers d ON ds.driver_id = d.id"
            " WHERE r.year = ?"
            " ORDER BY r.round, ds.points DESC",
            conn,
            params=[season],
        )
    records = df.to_dict(orient='records')
    for r in records:
        r['season'] = season
    return list(records)
