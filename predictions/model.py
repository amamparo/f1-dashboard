import numpy as np
from injector import inject
from sklearn.ensemble import GradientBoostingRegressor

from config import ModelConfig, PredictionResult


class RacePredictor:
    @inject
    def __init__(self, config: ModelConfig):
        self.config = config
        self._model: GradientBoostingRegressor | None = None

    def train(self, training_data: list[dict]) -> None:
        X_train = self._build_feature_matrix(training_data)
        y_train = np.array([float(r['actual_position']) for r in training_data])

        self._model = GradientBoostingRegressor(
            n_estimators=self.config.n_estimators,
            max_depth=self.config.max_depth,
            learning_rate=self.config.learning_rate,
            random_state=self.config.random_state,
        )
        self._model.fit(X_train, y_train)

    def predict(self, target_data: list[dict]) -> list[PredictionResult]:
        if self._model is None:
            raise RuntimeError('Model has not been trained. Call train() first.')

        X_target = self._build_feature_matrix(target_data)
        raw_scores = self._model.predict(X_target)
        positions = self._rank_to_positions(raw_scores)
        confidences = self._compute_confidences(raw_scores, positions)

        return [
            self._build_result(target_data[i], positions[i], confidences[i])
            for i in range(len(target_data))
        ]

    def _build_feature_matrix(self, rows: list[dict]) -> np.ndarray:
        return np.array([
            [float(row.get(col) or 0.0) for col in self.config.feature_columns]
            for row in rows
        ])

    @staticmethod
    def _rank_to_positions(raw_scores: np.ndarray) -> np.ndarray:
        positions = np.empty(len(raw_scores), dtype=int)
        for rank, idx in enumerate(np.argsort(raw_scores)):
            positions[idx] = rank + 1
        return positions

    @staticmethod
    def _compute_confidences(raw_scores: np.ndarray, positions: np.ndarray) -> np.ndarray:
        spread = np.abs(raw_scores - positions)
        max_spread = max(spread.max(), 1.0)
        return 1.0 - (spread / max_spread)

    def _build_result(self, row: dict, predicted: int, confidence: float) -> PredictionResult:
        actual = row.get('actual_position')
        grid = row.get('grid')
        predicted = int(predicted)
        return PredictionResult(
            driver_id=row['driver_id'],
            constructor_id=row.get('constructor_id'),
            grid=grid,
            predicted_position=predicted,
            actual_position=int(actual) if actual is not None else None,
            predicted_delta=int(grid) - predicted if grid is not None else None,
            actual_delta=(
                int(grid) - int(actual)
                if grid is not None and actual is not None
                else None
            ),
            confidence=round(float(confidence), 4),
            model_version=self.config.version,
        )
