from typing import Protocol

import requests
from injector import inject
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import PipelineConfig, PredictionResult

RETRY_STRATEGY = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET", "POST"],
)


class ApiClient(Protocol):
    def fetch_all_races(self) -> list[dict]: ...
    def fetch_season_race_ids(self, year: int) -> list[int]: ...
    def fetch_latest_season_year(self) -> int: ...
    def fetch_model_input(self, race_id: int) -> list[dict]: ...
    def post_predictions(self, race_id: int, predictions: list[PredictionResult]) -> dict: ...


class HttpApiClient:
    @inject
    def __init__(self, config: PipelineConfig):
        self.config = config
        self._session = requests.Session()
        self._session.mount("http://", HTTPAdapter(max_retries=RETRY_STRATEGY))
        self._session.mount("https://", HTTPAdapter(max_retries=RETRY_STRATEGY))

    def _get_json(self, path: str, params: dict | None = None) -> list | dict:
        resp = self._session.get(
            f'{self.config.api_url}{path}',
            params=params,
            timeout=self.config.request_timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def _post_json(self, path: str, payload: dict) -> dict:
        resp = self._session.post(
            f'{self.config.api_url}{path}',
            json=payload,
            timeout=self.config.request_timeout,
        )
        resp.raise_for_status()
        return resp.json()

    def fetch_all_races(self) -> list[dict]:
        return self._get_json('/races', params={
            'sort': '["id","DESC"]',
            'range': f'[0,{self.config.max_races_to_fetch - 1}]',
        })

    def fetch_season_race_ids(self, year: int) -> list[int]:
        races = self._get_json('/races', params={
            'filter': f'{{"year": {year}}}',
            'sort': '["round","ASC"]',
            'range': '[0,99]',
        })
        return [r['id'] for r in races]

    def fetch_latest_season_year(self) -> int:
        races = self._get_json('/races', params={
            'sort': '["id","DESC"]',
            'range': '[0,0]',
        })
        return races[0]['year']

    def fetch_model_input(self, race_id: int) -> list[dict]:
        return self._get_json(f'/predictions/model-input/{race_id}')

    def post_predictions(self, race_id: int, predictions: list[PredictionResult]) -> dict:
        payload = {
            'predictions': [
                {**p.to_dict(), 'race_id': race_id} for p in predictions
            ]
        }
        return self._post_json('/predictions', payload)
