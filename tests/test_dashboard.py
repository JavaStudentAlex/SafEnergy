import subprocess


def test_dashboard_syntax():
    """Verify that the Streamlit dashboard script has no syntax errors."""
    result = subprocess.run(
        ["python", "-m", "py_compile", "src/safenergy/api/dashboard.py"],
        capture_output=True,
    )
    assert result.returncode == 0, f"Syntax error in dashboard.py: {result.stderr.decode()}"
