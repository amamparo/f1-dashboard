from typing import List

from fastapi import APIRouter

from esm_fullstack_challenge.models import AutoGenModels
from esm_fullstack_challenge.routers.utils import \
    get_route_list_function, get_route_id_function


races_router = APIRouter()

table_model = AutoGenModels['races']

# Route to get race by id
get_race = get_route_id_function('races', table_model)
races_router.add_api_route(
    '/{id}', get_race,
    methods=["GET"], response_model=table_model,
)

# Route to get a list of races
get_races = get_route_list_function('races', table_model)
races_router.add_api_route(
    '', get_races,
    methods=["GET"], response_model=List[table_model],
)
