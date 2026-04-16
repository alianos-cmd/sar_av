CREATE TABLE geraet (
    device_id      BIGSERIAL PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    standort       VARCHAR(150),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE sensor (
    sensor_id       BIGSERIAL PRIMARY KEY,
    device_id       BIGINT NOT NULL,
    sensor_type     VARCHAR(30) NOT NULL,
    einheit         VARCHAR(20) NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'aktiv',
    installiert_am  TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_sensor_device
        FOREIGN KEY (device_id)
        REFERENCES geraet(device_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_sensor_type
        CHECK (sensor_type IN ('flamme', 'temperatur', 'feuchtigkeit', 'beben', 'luftqualitaet')),

    CONSTRAINT chk_sensor_status
        CHECK (status IN ('aktiv', 'inaktiv', 'wartung', 'defekt'))
);

CREATE TABLE messwert (
    mess_id         BIGSERIAL PRIMARY KEY,
    sensor_id       BIGINT NOT NULL,
    gemessen_am     TIMESTAMPTZ NOT NULL,
    wert_num        DOUBLE PRECISION,
    wert_bool       BOOLEAN,
    qualitaet       VARCHAR(20) NOT NULL DEFAULT 'ok',
    received_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    CONSTRAINT fk_messwert_sensor
        FOREIGN KEY (sensor_id)
        REFERENCES sensor(sensor_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_messwert_wert
        CHECK (
            (wert_num IS NOT NULL AND wert_bool IS NULL)
            OR
            (wert_num IS NULL AND wert_bool IS NOT NULL)
        ),

    CONSTRAINT chk_messwert_qualitaet
        CHECK (qualitaet IN ('ok', 'unsicher', 'fehlerhaft'))
);

CREATE TABLE alarm (
    alarm_id        BIGSERIAL PRIMARY KEY,
    sensor_id       BIGINT NOT NULL,
    alarm_art       VARCHAR(50) NOT NULL,
    alarm_wert      DOUBLE PRECISION,
    grenzwert       DOUBLE PRECISION,
    ausgeloest_am   TIMESTAMPTZ NOT NULL,
    beendet_am      TIMESTAMPTZ,

    CONSTRAINT fk_alarm_sensor
        FOREIGN KEY (sensor_id)
        REFERENCES sensor(sensor_id)
        ON DELETE CASCADE,

    CONSTRAINT chk_alarm_zeit
        CHECK (beendet_am IS NULL OR beendet_am >= ausgeloest_am)
);

CREATE INDEX idx_sensor_device_id
    ON sensor(device_id);

CREATE INDEX idx_messwert_sensor_zeit
    ON messwert(sensor_id, gemessen_am DESC);

CREATE INDEX idx_alarm_sensor_zeit
    ON alarm(sensor_id, ausgeloest_am DESC);