import logging
from typing import Optional, Protocol, Tuple, Union

import joblib
import lightgbm as lgb
import pandas as pd


class ForecastModel(Protocol):
    """Protocol for forecasting models."""

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """Fit the model to the training data."""
        ...

    def predict(self, X: pd.DataFrame) -> Union[pd.Series, pd.DataFrame]:
        """
        Predict the target variable.
        If uncertainty=True, should return a DataFrame with 'point', 'lower', 'upper' columns.
        If uncertainty=False, should return a Series with point predictions.
        """
        ...

    def save(self, filepath: str) -> None:
        """Save the model to disk."""
        ...

    @classmethod
    def load(cls, filepath: str) -> "ForecastModel":
        """Load the model from disk."""
        ...


class LightGBMForecaster:
    """
    LightGBM model for renewable generation and delta forecasting.
    Supports point forecasting and quantile-based uncertainty bounds.
    """

    def __init__(
        self,
        quantiles: Tuple[float, float, float] = (0.1, 0.5, 0.9),
        params: Optional[dict] = None,
    ):
        """
        Args:
            quantiles: Tuple of (lower, point, upper) quantiles for uncertainty.
            params: Optional dict of LightGBM hyper-parameters.
        """
        self.quantiles = quantiles
        self.lower_quantile = quantiles[0]
        self.point_quantile = quantiles[1]
        self.upper_quantile = quantiles[2]

        default_params = {
            "objective": "regression",
            "metric": "rmse",
            "n_estimators": 100,
            "random_state": 42,
            "verbose": -1,
        }
        self.params = params if params is not None else default_params

        # Models will be instantiated during fit
        self.model_lower = None
        self.model_point = None
        self.model_upper = None

    def fit(self, X: pd.DataFrame, y: pd.Series) -> None:
        """
        Fit quantile regression models.

        Args:
            X: Feature DataFrame.
            y: Target Series.
        """
        logging.info("Fitting LightGBM models for quantiles: %s", self.quantiles)

        # Fit lower bound
        params_lower = self.params.copy()
        params_lower.update({"objective": "quantile", "alpha": self.lower_quantile})
        self.model_lower = lgb.LGBMRegressor(**params_lower)
        self.model_lower.fit(X, y)

        # Fit point (median or specified point quantile)
        params_point = self.params.copy()
        if self.point_quantile == 0.5 and self.params.get("objective") in ("regression", "rmse"):
             # If using standard regression/RMSE, we stick to standard LightGBM for the point estimate
             pass
        else:
             params_point.update({"objective": "quantile", "alpha": self.point_quantile})

        self.model_point = lgb.LGBMRegressor(**params_point)
        self.model_point.fit(X, y)

        # Fit upper bound
        params_upper = self.params.copy()
        params_upper.update({"objective": "quantile", "alpha": self.upper_quantile})
        self.model_upper = lgb.LGBMRegressor(**params_upper)
        self.model_upper.fit(X, y)

    def predict(self, X: pd.DataFrame, return_uncertainty: bool = True) -> Union[pd.Series, pd.DataFrame]:
        """
        Predict target values.

        Args:
            X: Feature DataFrame.
            return_uncertainty: If True, returns a DataFrame with 'lower', 'point', 'upper'.
                                If False, returns a Series with 'point' predictions.

        Returns:
            Pandas Series or DataFrame indexed identically to X.
        """
        if self.model_point is None:
            raise ValueError("Model is not fitted yet. Call 'fit' first.")

        point_preds = self.model_point.predict(X)

        if not return_uncertainty:
            return pd.Series(point_preds, index=X.index, name="point")

        if self.model_lower is None or self.model_upper is None:
            raise ValueError("Quantile models are not fitted yet.")

        lower_preds = self.model_lower.predict(X)
        upper_preds = self.model_upper.predict(X)

        df_preds = pd.DataFrame(
            {
                "lower": lower_preds,
                "point": point_preds,
                "upper": upper_preds,
            },
            index=X.index,
        )

        # Ensure bounds are consistent (lower <= point <= upper) in edge cases
        df_preds["lower"] = df_preds[["lower", "point"]].min(axis=1)
        df_preds["upper"] = df_preds[["upper", "point"]].max(axis=1)

        return df_preds

    def save(self, filepath: str) -> None:
        """
        Serialize the LightGBMForecaster instance to a joblib file.

        Args:
            filepath: Path to save the model artifact.
        """
        logging.info("Saving LightGBMForecaster to %s", filepath)
        joblib.dump(self, filepath)

    @classmethod
    def load(cls, filepath: str) -> "LightGBMForecaster":
        """
        Load a LightGBMForecaster instance from a joblib file.

        Args:
            filepath: Path to the saved model artifact.

        Returns:
            The loaded LightGBMForecaster instance.
        """
        logging.info("Loading LightGBMForecaster from %s", filepath)
        model = joblib.load(filepath)
        if not isinstance(model, cls):
            raise TypeError(f"Loaded object is not an instance of {cls.__name__}")
        return model
