import os
import sys
import pytest

# Ensure webapp directory is in sys.path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from app import app, predict_species, model, target_names


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_model_loaded():
    """Verify that model is loaded and target names exist."""
    assert model is not None, "Model was not loaded successfully."
    assert "setosa" in target_names
    assert "versicolor" in target_names
    assert "virginica" in target_names


def test_predict_species_direct():
    """Test the prediction logic directly with known Iris-setosa sample."""
    setosa_sample = [5.1, 3.5, 1.4, 0.2]
    result = predict_species(setosa_sample)
    assert result.lower() == "setosa"


def test_health_endpoint(client):
    """Test the /health endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_home_page(client):
    """Test the GET / home page."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Iris Flower Classifier" in response.data


def test_predict_json_success(client):
    """Test POST /predict with valid JSON payload."""
    payload = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["prediction"].lower() == "setosa"


def test_predict_form_success(client):
    """Test POST /predict with valid HTML form data."""
    form_data = {
        "sepal_length": "6.7",
        "sepal_width": "3.0",
        "petal_length": "5.2",
        "petal_width": "2.3"
    }
    response = client.post("/predict", data=form_data)
    assert response.status_code == 200
    assert b"Iris-virginica" in response.data or b"virginica" in response.data


def test_predict_invalid_input(client):
    """Test POST /predict with invalid data (e.g., text instead of number)."""
    invalid_payload = {
        "sepal_length": "invalid_number",
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 400


def test_records_page(client):
    """Test GET /records page renders successfully."""
    response = client.get("/records")
    assert response.status_code == 200
    assert b"Database Prediction Records" in response.data
