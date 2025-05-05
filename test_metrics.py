from datetime import datetime, timezone
import uuid

# Función para generar métricas falsas
def generar_metrica_falsa(server_id="web01"):
    return {
        "server_id": server_id,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),  # Modificado aquí
        "metrics": {
            "cpu_percent": 42.5,
            "memory_percent": 68.2,
            "disk_io_mbps": 15.3,
            "network_mbps": 23.1,
            "error_count": 0
        },
        "message_uuid": str(uuid.uuid4())
    }

# Test para validar el formato de métricas
def test_formato_metrica():
    metrica = generar_metrica_falsa()
    assert "server_id" in metrica, "Falta la clave 'server_id'"
    assert "timestamp_utc" in metrica, "Falta la clave 'timestamp_utc'"
    assert "metrics" in metrica, "Falta la clave 'metrics'"
    assert isinstance(metrica["metrics"]["cpu_percent"], float), "cpu_percent no es float"
    assert 0 <= metrica["metrics"]["cpu_percent"] <= 100, "cpu_percent fuera de rango [0-100]"
    print("[OK] test_formato_metrica superado.")

# Test para validar que los UUID son únicos
def test_uuid_unico():
    ids = {generar_metrica_falsa()["message_uuid"] for _ in range(100)}
    assert len(ids) == 100, "UUID duplicados detectados"
    print("[OK] test_uuid_unico superado.")

# Bloque para ejecutar tests manualmente con Python
if __name__ == "__main__":
    try:
        test_formato_metrica()
        test_uuid_unico()
        print("\n✅ Todos los tests han pasado correctamente.")
    except AssertionError as e:
        print(f"\n❌ Test fallido: {e}")
