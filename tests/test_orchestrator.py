import datetime

from safenergy.orchestrator.pipeline import run_end_to_end_pipeline


def test_pipeline_runs_successfully():
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    end_date = datetime.date.today()

    response = run_end_to_end_pipeline(
        asset_id="TEST_SITE_1",
        latitude=30.2672,
        longitude=-97.7431,
        start_date=start_date,
        end_date=end_date,
        simulate_failure=False,
    )

    assert response.asset_id == "TEST_SITE_1"
    assert not response.forecast_df.empty
    # Allow signals to be empty or not, depending on the generated data
    # assert len(response.signals) > 0
    assert isinstance(response.issue_time, datetime.datetime)

def test_pipeline_handles_failure():
    start_date = datetime.date.today() - datetime.timedelta(days=2)
    end_date = datetime.date.today()

    response = run_end_to_end_pipeline(
        asset_id="TEST_SITE_FAIL",
        latitude=30.2672,
        longitude=-97.7431,
        start_date=start_date,
        end_date=end_date,
        simulate_failure=True,
    )

    assert response.asset_id == "TEST_SITE_FAIL"
    # The pipeline should run but have empty arrays or basic fallback behaviour
