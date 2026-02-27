import json
import logging
import sys

import requests
from injector import Injector, Module, inject, provider, singleton

from api_client import ApiClient, HttpApiClient
from config import ModelConfig, PipelineConfig
from model import RacePredictor

logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')
logger = logging.getLogger(__name__)


class PredictionPipeline:
    @inject
    def __init__(self, api: ApiClient, predictor: RacePredictor, config: PipelineConfig):
        self.api = api
        self.predictor = predictor
        self.config = config

    def run(self, event: dict | None = None) -> dict:
        event = event or {}
        race_id = event.get('race_id')
        season = event.get('season')

        season, race_ids = self._resolve_race_ids(race_id, season)
        if not race_id:
            logger.info('Predicting season %d (%d races)', season, len(race_ids))

        training_data = self._fetch_training_data(exclude_race_ids=race_ids)
        if len(training_data) < self.config.min_training_rows:
            return {'status': 'skip', 'reason': 'Insufficient training data'}

        logger.info('Training on %d rows', len(training_data))
        self.predictor.train(training_data)

        total = sum(
            count for rid in race_ids
            if (count := self._predict_and_post(rid)) is not None
        )

        logger.info('Done: %d predictions across %d races', total, len(race_ids))
        return {
            'status': 'ok',
            'season': season,
            'races': len(race_ids),
            'predictions_count': total,
        }

    def _resolve_race_ids(
        self, race_id: int | None, season: int | None,
    ) -> tuple[int | None, list[int]]:
        if race_id is not None:
            return season, [race_id]
        if season is None:
            season = self.api.fetch_latest_season_year()
        return season, self.api.fetch_season_race_ids(season)

    def _fetch_training_data(self, exclude_race_ids: list[int]) -> list[dict]:
        excluded = set(exclude_race_ids)
        races = self.api.fetch_all_races()
        eligible_races = [
            r for r in races
            if r.get('year', 0) >= self.config.min_training_year
            and r['id'] not in excluded
        ]

        all_rows = []
        for race in eligible_races:
            try:
                rows = self.api.fetch_model_input(race['id'])
                all_rows.extend(r for r in rows if r.get('actual_position') is not None)
            except requests.HTTPError as exc:
                logger.warning('Failed to fetch model input for race %d: %s', race['id'], exc)
                continue
        return all_rows

    def _predict_and_post(self, race_id: int) -> int | None:
        target_data = self.api.fetch_model_input(race_id)
        if not target_data:
            logger.warning('Skipping race %d: no data', race_id)
            return None

        logger.info('Predicting race %d (%d drivers)', race_id, len(target_data))
        predictions = self.predictor.predict(target_data)
        self.api.post_predictions(race_id, predictions)
        return len(predictions)


class PredictionModule(Module):
    def configure(self, binder):
        binder.bind(ApiClient, to=HttpApiClient)

    @singleton
    @provider
    def provide_pipeline_config(self) -> PipelineConfig:
        return PipelineConfig()

    @singleton
    @provider
    def provide_model_config(self) -> ModelConfig:
        return ModelConfig()


def handler(event, context=None):
    try:
        injector = Injector([PredictionModule()])
        pipeline = injector.get(PredictionPipeline)
        return pipeline.run(event)
    except Exception:
        logger.exception('Prediction pipeline failed')
        return {'status': 'error', 'reason': 'Unhandled exception (see logs)'}


if __name__ == '__main__':
    arg = int(sys.argv[1]) if len(sys.argv) > 1 else None
    if arg and arg >= 1950:
        event = {'season': arg}
    elif arg:
        event = {'race_id': arg}
    else:
        event = {}
    result = handler(event)
    print(json.dumps(result, indent=2))
