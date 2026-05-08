from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import psycopg2
from datetime import datetime, timezone

app = Flask(__name__)

UPLOAD_DIR = "/var/www/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

DB_HOST = "127.0.0.1"
DB_NAME = "eure_datenbank"
DB_USER = "euer_user"
DB_PASSWORD = "euer_passwort"
DB_PORT = 5432


def db_connect():
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


@app.route("/api/upload/", methods=["POST"])
def upload():
    file = request.files["datei"]
    filename = secure_filename(file.filename)
    path = os.path.join(UPLOAD_DIR, filename)
    file.save(path)

    return jsonify({
        "ok": True,
        "dateiname": filename
    })


@app.route("/sensor", methods=["POST"])
def sensor():
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"status": "fehler", "meldung": "Kein JSON empfangen"}), 400

    device_name = data.get("device")
    temp = data.get("temp")
    hum = data.get("hum")
    gas = data.get("gas")

    if not device_name:
        return jsonify({"status": "fehler", "meldung": "device fehlt"}), 400

    measured_at = datetime.now(timezone.utc)

    conn = None
    cur = None

    try:
        conn = db_connect()
        cur = conn.cursor()

        cur.execute(
            """
            SELECT device_id
            FROM geraet
            WHERE name = %s
            """,
            (device_name,)
        )
        device_row = cur.fetchone()

        if not device_row:
            return jsonify({
                "status": "fehler",
                "meldung": f"Geraet '{device_name}' nicht gefunden"
            }), 404

        device_id = device_row[0]

        cur.execute(
            """
            SELECT sensor_id, sensor_type
            FROM sensor
            WHERE device_id = %s
              AND status = 'aktiv'
            """,
            (device_id,)
        )
        sensor_rows = cur.fetchall()

        sensors = {}
        for sensor_id, sensor_type in sensor_rows:
            sensors[sensor_type] = sensor_id

        gespeichert = 0

        if temp is not None and "temperatur" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["temperatur"], measured_at, float(temp), "ok")
            )
            gespeichert += 1

        if hum is not None and "feuchtigkeit" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["feuchtigkeit"], measured_at, float(hum), "ok")
            )
            gespeichert += 1

        if gas is not None and "luftqualitaet" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["luftqualitaet"], measured_at, float(gas), "ok")
            )
            gespeichert += 1

        conn.commit()

        return jsonify({
            "status": "ok",
            "geraet": device_name,
            "gespeichert": gespeichert
        }), 200

    except Exception as e:
        if conn:
            conn.rollback()

        return jsonify({
            "status": "fehler",
            "meldung": str(e)
        }), 500

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


@app.route("/", methods=["GET"])
def index():
    return "Flask-App läuft."


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)