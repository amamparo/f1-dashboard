from typing import List

from fastapi import APIRouter

from esm_fullstack_challenge.dependencies import get_db
from esm_fullstack_challenge.models import AutoGenModels
from esm_fullstack_challenge.models.utils import get_all_table_names
from esm_fullstack_challenge.routers.utils import \
    get_route_list_function, get_route_id_function


def add_basic_routes(
        router: APIRouter,
        exclude_tables: list[str] | None = None
):
    """Adds basic endpoint routes to a route for listing all items or
       getting a single item by id.

    Args:
        router (APIRouter): FastAPI router to add routes to
        exclude_tables (list[str] | None, optional): List of tables to skip. Defaults to None.
    """
    db = next(get_db())
    with db.get_connection() as conn:
        table_names = get_all_table_names(conn)

        for table in table_names:
            if exclude_tables and table in exclude_tables:
                continue
            table_model = AutoGenModels[table]

            route_list_func = get_route_list_function(
                table, table_model
            )
            router.add_api_route(
                f'/{table}',
                route_list_func,
                methods=["GET"],
                response_model=List[table_model],
            )

            route_id_function = get_route_id_function(table, table_model)
            router.add_api_route(
                f'/{table}/' + '{id}',
                route_id_function,
                methods=["GET"],
                response_model=table_model,
            )


basic_router = APIRouter()
add_basic_routes(basic_router, exclude_tables=['drivers', 'races'])
