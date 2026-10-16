import os
import pickle
import numpy as np
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Base directory and model path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

def get_db_service_url():
    return os.environ.get("DB_SERVICE_URL", "http://dbapp:5002")

# Load trained model
loaded_data = None
model = None
target_names = ["setosa", "versicolor", "virginica"]

if os.path.exists(MODEL_PATH):
    try:
        with open(MODEL_PATH, "rb") as f:
            loaded_data = pickle.load(f)
            if isinstance(loaded_data, dict) and "model" in loaded_data:
                model = loaded_data["model"]
                target_names = loaded_data.get("target_names", target_names)
            else:
                model = loaded_data
    except Exception as e:
        print(f"Warning: Failed to load model.pkl: {e}")


def predict_species(features_list):
    """Predict iris species name from 4 numeric features."""
    if model is None:
        raise RuntimeError("Model is not loaded.")
    X = np.array([features_list], dtype=float)
    raw_pred = model.predict(X)[0]
    if isinstance(raw_pred, (int, np.integer)):
        species_name = target_names[int(raw_pred)]
    else:
        species_name = str(raw_pred)
    return species_name


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "service": "webapp",
        "model_loaded": model is not None
    })


@app.route("/predict", methods=["POST"])
def predict():
    # Support both JSON requests and HTML form submissions
    is_json = request.is_json

    if is_json:
        data = request.get_json() or {}
        try:
            sl = float(data["sepal_length"])
            sw = float(data["sepal_width"])
            pl = float(data["petal_length"])
            pw = float(data["petal_width"])
        except (KeyError, ValueError, TypeError) as e:
            return jsonify({"status": "error", "message": f"Invalid feature values: {e}"}), 400
    else:
        try:
            sl = float(request.form.get("sepal_length", 0))
            sw = float(request.form.get("sepal_width", 0))
            pl = float(request.form.get("petal_length", 0))
            pw = float(request.form.get("petal_width", 0))
        except (ValueError, TypeError) as e:
            return render_template(
                "index.html",
                error=f"Invalid numeric input: {e}",
                inputs=request.form
            ), 400

    try:
        prediction_name = predict_species([sl, sw, pl, pw])
    except Exception as err:
        if is_json:
            return jsonify({"status": "error", "message": str(err)}), 500
        return render_template("index.html", error=f"Prediction error: {err}", inputs=request.form), 500

    # Attempt to persist record to dbapp microservice
    db_status = "Not saved"
    payload = {
        "sepal_length": sl,
        "sepal_width": sw,
        "petal_length": pl,
        "petal_width": pw,
        "prediction": prediction_name
    }

    try:
        db_url = get_db_service_url()
        resp = requests.post(f"{db_url}/save", json=payload, timeout=2)
        if resp.status_code in (200, 201):
            db_status = "Saved to Database"
        else:
            db_status = f"Database responded with code {resp.status_code}"
    except Exception:
        db_status = "Database service currently unavailable (prediction succeeded)"

    if is_json:
        return jsonify({
            "status": "success",
            "sepal_length": sl,
            "sepal_width": sw,
            "petal_length": pl,
            "petal_width": pw,
            "prediction": prediction_name,
            "db_status": db_status
        }), 200

    return render_template(
        "index.html",
        prediction=prediction_name,
        db_status=db_status,
        inputs={
            "sepal_length": sl,
            "sepal_width": sw,
            "petal_length": pl,
            "petal_width": pw
        }
    )


@app.route("/records", methods=["GET"])
def display_records():
    records = []
    error_message = None

    db_url = get_db_service_url()
    try:
        resp = requests.get(f"{db_url}/predictions", timeout=3)
        if resp.status_code == 200:
            records = resp.json()
        else:
            error_message = f"Database service returned error {resp.status_code}"
    except Exception as e:
        error_message = f"Could not reach database service at {db_url}. Ensure dbapp is running."

    return render_template(
        "display_records.html",
        records=records,
        error_message=error_message
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
