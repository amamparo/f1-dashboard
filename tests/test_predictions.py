import pytest
from injector import Injector, Module, provider, singleton

from api_client import ApiClient, HttpApiClient
from config import ModelConfig, PipelineConfig, PredictionResult
from handler import PredictionPipeline
from model import RacePredictor


SAMPLE_TRAINING_DATA = [
    {
        'driver_id': i,
        'constructor_id': 1,
        'grid': i,
        'actual_position': i,
        'championship_points': 100 - i * 5,
        'championship_position': i,
        'season_wins': max(5 - i, 0),
        'circuit_lat': 51.5,
        'circuit_lng': -0.1,
        'circuit_altitude': 100,
    }
    for i in range(1, 21)
] * 5  # 100 rows of training data


SAMPLE_TARGET_DATA = [
    {
        'driver_id': i,
        'constructor_id': 1,
        'grid': i,
        'actual_position': i,
        'championship_points': 100 - i * 5,
        'championship_position': i,
        'season_wins': max(5 - i, 0),
        'circuit_lat': 40.0,
        'circuit_lng': -3.7,
        'circuit_altitude': 650,
    }
    for i in range(1, 6)
]

SAMPLE_RACES = [
    {'id': 100 + i, 'year': 2020, 'round': i, 'name': f'Race {i}'}
    for i in range(1, 4)
] + [
    {'id': 200 + i, 'year': 2019, 'round': i, 'name': f'Training Race {i}'}
    for i in range(1, 6)
]


class FakeApiClient:
    def __init__(self):
        self.races = list(SAMPLE_RACES)
        self.model_inputs: dict[int, list[dict]] = {
            r['id']: list(SAMPLE_TRAINING_DATA[:20])
            for r in self.races
        }
        self.posted_predictions: list[dict] = []

    def fetch_all_races(self):
        return self.races

    def fetch_season_race_ids(self, year):
        return [r['id'] for r in self.races if r['year'] == year]

    def fetch_latest_season_year(self):
        return max(r['year'] for r in self.races)

    def fetch_model_input(self, race_id):
        return self.model_inputs.get(race_id, [])

    def post_predictions(self, race_id, predictions):
        self.posted_predictions.append({
            'race_id': race_id,
            'predictions': predictions,
        })
        return {'status': 'ok', 'count': len(predictions)}


class TestModelConfig:
    def test_defaults(self):
        config = ModelConfig()
        assert config.n_estimators == 200
        assert config.max_depth == 4
        assert config.learning_rate == 0.1
        assert config.random_state == 42
        assert config.version == 'gbr-v1'
        assert 'grid' in config.feature_columns

    def test_custom_values(self):
        config = ModelConfig(n_estimators=50, version='test-v1')
        assert config.n_estimators == 50
        assert config.version == 'test-v1'

    def test_frozen(self):
        config = ModelConfig()
        with pytest.raises(AttributeError):
            config.version = 'modified'


class TestPipelineConfig:
    def test_defaults(self):
        config = PipelineConfig()
        assert config.min_training_year == 2015
        assert config.min_training_rows == 50
        assert config.request_timeout == 30

    def test_custom_api_url(self):
        config = PipelineConfig(api_url='http://test:8080')
        assert config.api_url == 'http://test:8080'


class TestPredictionResult:
    def test_to_dict(self):
        result = PredictionResult(
            driver_id=1,
            predicted_position=3,
            model_version='test-v1',
            grid=5,
            confidence=0.85,
        )
        d = result.to_dict()
        assert d['driver_id'] == 1
        assert d['predicted_position'] == 3
        assert d['model_version'] == 'test-v1'
        assert d['grid'] == 5
        assert d['confidence'] == 0.85
        assert d['actual_position'] is None

    def test_frozen(self):
        result = PredictionResult(driver_id=1, predicted_position=1, model_version='v1')
        with pytest.raises(AttributeError):
            result.driver_id = 2


class TestRacePredictor:
    @pytest.fixture
    def predictor(self):
        p = RacePredictor(ModelConfig(n_estimators=10, max_depth=2))
        p.train(SAMPLE_TRAINING_DATA)
        return p

    def test_predict_returns_correct_count(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        assert len(results) == len(SAMPLE_TARGET_DATA)

    def test_predict_returns_prediction_results(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        for r in results:
            assert isinstance(r, PredictionResult)

    def test_positions_are_unique_and_complete(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        positions = sorted(r.predicted_position for r in results)
        assert positions == list(range(1, len(SAMPLE_TARGET_DATA) + 1))

    def test_confidences_are_bounded(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        for r in results:
            assert 0.0 <= r.confidence <= 1.0

    def test_model_version_from_config(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        for r in results:
            assert r.model_version == 'gbr-v1'

    def test_predicted_delta_computed_correctly(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        for r in results:
            if r.grid is not None:
                assert r.predicted_delta == r.grid - r.predicted_position

    def test_actual_delta_computed_correctly(self, predictor):
        results = predictor.predict(SAMPLE_TARGET_DATA)
        for r in results:
            if r.grid is not None and r.actual_position is not None:
                assert r.actual_delta == r.grid - r.actual_position

    def test_handles_missing_grid(self, predictor):
        results = predictor.predict([{'driver_id': 1, 'actual_position': 1}])
        assert results[0].grid is None
        assert results[0].predicted_delta is None
        assert results[0].actual_delta is None

    def test_handles_missing_actual_position(self, predictor):
        results = predictor.predict([{'driver_id': 1, 'grid': 5}])
        assert results[0].actual_position is None
        assert results[0].actual_delta is None

    def test_predict_before_train_raises(self):
        predictor = RacePredictor(ModelConfig(n_estimators=10, max_depth=2))
        with pytest.raises(RuntimeError, match='not been trained'):
            predictor.predict(SAMPLE_TARGET_DATA)


class TestPredictionPipeline:
    @pytest.fixture
    def fake_api(self):
        return FakeApiClient()

    @pytest.fixture
    def pipeline(self, fake_api):
        config = PipelineConfig(
            api_url='http://fake',
            min_training_rows=5,
            min_training_year=2015,
        )
        predictor = RacePredictor(ModelConfig(n_estimators=10, max_depth=2))
        return PredictionPipeline(
            api=fake_api,
            predictor=predictor,
            config=config,
        )

    def test_single_race_prediction(self, pipeline, fake_api):
        fake_api.model_inputs[101] = list(SAMPLE_TARGET_DATA)
        result = pipeline.run({'race_id': 101})
        assert result['status'] == 'ok'
        assert result['predictions_count'] == 5
        assert len(fake_api.posted_predictions) == 1
        assert fake_api.posted_predictions[0]['race_id'] == 101

    def test_season_prediction(self, pipeline, fake_api):
        for race in fake_api.races:
            fake_api.model_inputs[race['id']] = list(SAMPLE_TARGET_DATA)
        result = pipeline.run({'season': 2020})
        assert result['status'] == 'ok'
        assert result['races'] == 3
        assert result['predictions_count'] == 15
        assert len(fake_api.posted_predictions) == 3

    def test_latest_season_when_no_event(self, pipeline, fake_api):
        for race in fake_api.races:
            fake_api.model_inputs[race['id']] = list(SAMPLE_TARGET_DATA)
        result = pipeline.run({})
        assert result['status'] == 'ok'
        assert result['season'] == 2020

    def test_skips_when_insufficient_training_data(self, fake_api):
        config = PipelineConfig(
            api_url='http://fake',
            min_training_rows=999999,
        )
        predictor = RacePredictor(ModelConfig(n_estimators=10, max_depth=2))
        pipeline = PredictionPipeline(api=fake_api, predictor=predictor, config=config)
        result = pipeline.run({'race_id': 101})
        assert result['status'] == 'skip'

    def test_skips_race_with_no_target_data(self, pipeline, fake_api):
        fake_api.model_inputs[101] = []
        result = pipeline.run({'race_id': 101})
        assert result['predictions_count'] == 0

    def test_injector_wiring(self):
        class TestModule(Module):
            def __init__(self, fake_api):
                self._fake_api = fake_api

            def configure(self, binder):
                binder.bind(ApiClient, to=lambda: self._fake_api)

            @singleton
            @provider
            def provide_pipeline_config(self) -> PipelineConfig:
                return PipelineConfig(api_url='http://fake', min_training_rows=5)

            @singleton
            @provider
            def provide_model_config(self) -> ModelConfig:
                return ModelConfig(n_estimators=10, max_depth=2)

        fake_api = FakeApiClient()
        for race in fake_api.races:
            fake_api.model_inputs[race['id']] = list(SAMPLE_TARGET_DATA)

        injector = Injector([TestModule(fake_api)])
        pipeline = injector.get(PredictionPipeline)
        result = pipeline.run({'race_id': 101})
        assert result['status'] == 'ok'
        assert len(fake_api.posted_predictions) == 1
