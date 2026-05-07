from flask import Flask, request, jsonify
import psycopg2
from datetime import datetime, timezone

app = Flask(__name__)

# ===== Datenbank-Zugang =====
# Hier eure echten Zugangsdaten eintragen
DB_HOST = "127.0.0.1"
DB_NAME = "eure_datenbank"
DB_USER = "euer_user"
DB_PASSWORD = "euer_passwort"
DB_PORT = 5432


def db_connect():
    # Baut eine Verbindung zur PostgreSQL-Datenbank auf
    return psycopg2.connect(
        host=DB_HOST,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )


@app.route("/sensor", methods=["POST"])
def sensor():
    # JSON aus dem Request lesen
    data = request.get_json(silent=True)

    # Falls gar kein JSON angekommen ist -> Fehler
    if not data:
        return jsonify({"status": "fehler", "meldung": "Kein JSON empfangen"}), 400

    # Werte aus dem JSON holen
    device_name = data.get("device")
    temp = data.get("temp")
    hum = data.get("hum")
    gas = data.get("gas")

    # Ohne Gerätenamen wissen wir nicht,
    # wohin die Daten in der Datenbank gehören
    if not device_name:
        return jsonify({"status": "fehler", "meldung": "device fehlt"}), 400

    # Zeitpunkt der Messung
    measured_at = datetime.now(timezone.utc)

    conn = None
    cur = None

    try:
        # Mit Datenbank verbinden
        conn = db_connect()
        cur = conn.cursor()

        # ===== 1. Gerät suchen =====
        cur.execute(
            """
            SELECT device_id
            FROM geraet
            WHERE name = %s
            """,
            (device_name,)
        )

        device_row = cur.fetchone()

        # Wenn das Gerät nicht existiert -> Fehler
        if not device_row:
            return jsonify({
                "status": "fehler",
                "meldung": f"Geraet '{device_name}' nicht gefunden"
            }), 404

        device_id = device_row[0]

        # ===== 2. Sensoren dieses Geräts laden =====
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

        # Aus den Daten ein Wörterbuch bauen:
        # z. B. sensors["temperatur"] = 7
        sensors = {}
        for sensor_id, sensor_type in sensor_rows:
            sensors[sensor_type] = sensor_id

        gespeichert = 0

        # ===== 3. Temperatur speichern =====
        if temp is not None and "temperatur" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["temperatur"], measured_at, float(temp), "ok")
            )
            gespeichert += 1

        # ===== 4. Feuchtigkeit speichern =====
        if hum is not None and "feuchtigkeit" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["feuchtigkeit"], measured_at, float(hum), "ok")
            )
            gespeichert += 1

        # ===== 5. Luftqualität / Gas speichern =====
        if gas is not None and "luftqualitaet" in sensors:
            cur.execute(
                """
                INSERT INTO messwert (sensor_id, gemessen_am, wert_num, qualitaet)
                VALUES (%s, %s, %s, %s)
                """,
                (sensors["luftqualitaet"], measured_at, float(gas), "ok")
            )
            gespeichert += 1

        # Alles endgültig speichern
        conn.commit()

        return jsonify({
            "status": "ok",
            "geraet": device_name,
            "gespeichert": gespeichert
        }), 200

    except Exception as e:
        # Falls Fehler passieren: Änderungen zurückrollen
        if conn:
            conn.rollback()

        return jsonify({
            "status": "fehler",
            "meldung": str(e)
        }), 500

    finally:
        # Verbindung sauber schließen
        if cur:
            cur.close()
        if conn:
            conn.close()


# Nur fürs lokale Testen
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)