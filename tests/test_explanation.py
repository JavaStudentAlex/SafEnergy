
from safenergy.signals.explanation import generate_explanation


def test_generate_explanation_basic():
    response = generate_explanation(
        forecast_delta=15.0,
        baseline=100.0,
        lower_bound=105.0,
        upper_bound=125.0
    )
    assert response.uncertainty_mw == 20.0
    assert response.confidence == "Medium"
    assert "15.0 MW higher" in response.summary
    assert not response.top_drivers


def test_generate_explanation_low_confidence():
    response = generate_explanation(
        forecast_delta=-5.0,
        baseline=10.0,
        lower_bound=-10.0,
        upper_bound=20.0
    )
    assert response.uncertainty_mw == 30.0
    assert response.confidence == "Low"
    assert "5.0 MW lower" in response.summary


def test_generate_explanation_with_features():
    features = {
        "cloud_cover": -10.0,
        "wind_speed": 5.0,
        "temperature": -2.0,
        "solar_irradiance": 8.0,
    }
    response = generate_explanation(
        forecast_delta=0.0,
        baseline=50.0,
        lower_bound=45.0,
        upper_bound=55.0,
        features=features
    )
    assert response.uncertainty_mw == 10.0
    assert len(response.top_drivers) == 3
    # Top 3 based on absolute values: cloud_cover (-10), solar_irradiance (8), wind_speed (5)
    assert "cloud_cover" in response.top_drivers
    assert "solar_irradiance" in response.top_drivers
    assert "wind_speed" in response.top_drivers

    assert len(response.attribution) == 3
    for attr in response.attribution:
        if attr.feature_name == "cloud_cover":
            assert attr.contribution_mw == -10.0
            assert "Decreases" in attr.description


def test_generate_explanation_with_market_price():
    response = generate_explanation(
        forecast_delta=20.0,
        baseline=50.0,
        lower_bound=60.0,
        upper_bound=80.0,
        market_price=-15.0
    )
    assert "negative (-15.00)" in response.summary
    assert "curtailment" in response.summary

    response_high = generate_explanation(
        forecast_delta=20.0,
        baseline=50.0,
        lower_bound=60.0,
        upper_bound=80.0,
        market_price=250.0
    )
    assert "high (250.00)" in response_high.summary
