import os
import sqlite3
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "data.db"))


def init_db():
    db_dir = os.path.dirname(os.path.abspath(DB_PATH))
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sepal_length REAL,
            sepal_width REAL,
            petal_length REAL,
            petal_width REAL,
            prediction TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "service": "dbapp"})


@app.route("/save", methods=["POST"])
def save_prediction():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No JSON payload provided"}), 400

    sepal_length = data.get("sepal_length")
    sepal_width = data.get("sepal_width")
    petal_length = data.get("petal_length")
    petal_width = data.get("petal_width")
    prediction = data.get("prediction")

    if prediction is None:
        return jsonify({"status": "error", "message": "Missing prediction value"}), 400

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO predictions (sepal_length, sepal_width, petal_length, petal_width, prediction)
        VALUES (?, ?, ?, ?, ?)
    """, (sepal_length, sepal_width, petal_length, petal_width, str(prediction)))
    conn.commit()
    inserted_id = cursor.lastrowid
    conn.close()

    return jsonify({
        "status": "success",
        "message": "Prediction saved successfully",
        "record_id": inserted_id
    }), 201


@app.route("/predictions", methods=["GET"])
def get_predictions():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, sepal_length, sepal_width, petal_length, petal_width, prediction, timestamp
        FROM predictions
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    conn.close()

    records = [
        {
            "id": row[0],
            "sepal_length": row[1],
            "sepal_width": row[2],
            "petal_length": row[3],
            "petal_width": row[4],
            "prediction": row[5],
            "timestamp": row[6]
        }
        for row in rows
    ]

    return jsonify(records), 200


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=True)
