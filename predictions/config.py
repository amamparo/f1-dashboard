import os
from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class PredictionResult:
    driver_id: int
    predicted_position: int
    model_version: str
    constructor_id: int | None = None
    grid: int | None = None
    actual_position: int | None = None
    predicted_delta: int | None = None
    actual_delta: int | None = None
    confidence: float | None = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(frozen=True)
class ModelConfig:
    feature_columns: tuple[str, ...] = (
        'grid',
        'championship_points',
        'championship_position',
        'season_wins',
        'circuit_lat',
        'circuit_lng',
        'circuit_altitude',
    )
    n_estimators: int = 200
    max_depth: int = 4
    learning_rate: float = 0.1
    random_state: int = 42
    version: str = 'gbr-v1'


@dataclass(frozen=True)
class PipelineConfig:
    api_url: str = field(
        default_factory=lambda: os.environ.get('API_URL', 'http://localhost:9000')
    )
    min_training_year: int = 2015
    min_training_rows: int = 50
    max_races_to_fetch: int = 1000
    request_timeout: int = 30
