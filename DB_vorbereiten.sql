-- 1) Gerät anlegen
INSERT INTO geraet (name, standort)
VALUES ('az-envy-01', 'Hannover');

-- 2) Prüfen, welche device_id das Gerät bekommen hat
SELECT * FROM geraet WHERE name = 'az-envy-01';

-- 3) Sensoren für dieses Gerät anlegen
-- HIER die device_id einsetzen, z. B. 1
INSERT INTO sensor (device_id, sensor_type, einheit, status)
VALUES
(1, 'temperatur', '°C', 'aktiv'),
(1, 'feuchtigkeit', '%', 'aktiv'),
(1, 'luftqualitaet', 'raw', 'aktiv');

-- 4) Kontrolle
SELECT * FROM sensor WHERE device_id = 1;