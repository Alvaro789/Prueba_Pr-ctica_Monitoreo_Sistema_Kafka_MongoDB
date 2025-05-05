import random
import time
from datetime import datetime, timezone
import uuid
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

# --- Configuración ---
SERVER_IDS = ["web01", "web02", "db01", "app01", "cache01"]
REPORTING_INTERVAL_SECONDS = 10
KAFKA_TOPIC = "system-metrics-topic-iabd10"
KAFKA_BROKER = "172.18.48.1:29092"  

# --- Configurar Kafka Producer ---
def create_producer():
    try:
        producer = KafkaProducer(
            bootstrap_servers=[KAFKA_BROKER],
            value_serializer=lambda v: json.dumps(v).encode("utf-8")
        )
        print(f" Conectado a Kafka en {KAFKA_BROKER}")
        return producer
    except Exception as e:
        print(f"Error conectando a Kafka: {e}")
        exit(1)

# --- Inicio del Script ---
if __name__ == "__main__":
    print(" Iniciando simulación de generación y envío de métricas a Kafka...")
    print(f"Servidores simulados: {SERVER_IDS}")
    print(f"Intervalo de reporte: {REPORTING_INTERVAL_SECONDS} segundos")
    print("-" * 40)

    producer = create_producer()

    try:
        while True:
            print(f"\n {datetime.now()}: Generando y enviando métricas...")
            for server_id in SERVER_IDS:
                cpu_percent = random.uniform(5.0, 75.0)
                if random.random() < 0.1:
                    cpu_percent = random.uniform(85.0, 98.0)

                memory_percent = random.uniform(20.0, 85.0)
                if random.random() < 0.05:
                    memory_percent = random.uniform(90.0, 99.0)

                disk_io_mbps = random.uniform(0.1, 50.0)
                network_mbps = random.uniform(1.0, 100.0)
                error_count = random.randint(1, 3) if random.random() < 0.08 else 0

                metric_message = {
                    "server_id": server_id,
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "metrics": {
                        "cpu_percent": round(cpu_percent, 2),
                        "memory_percent": round(memory_percent, 2),
                        "disk_io_mbps": round(disk_io_mbps, 2),
                        "network_mbps": round(network_mbps, 2),
                        "error_count": error_count
                    },
                    "message_uuid": str(uuid.uuid4())
                }

                try:
                    producer.send(KAFKA_TOPIC, metric_message)
                    print(f" Enviada métrica de {server_id} a Kafka.")
                except KafkaError as e:
                    print(f" Error enviando métrica de {server_id}: {e}")

            print(f" Esperando {REPORTING_INTERVAL_SECONDS} segundos antes del siguiente envío...\n")
            time.sleep(REPORTING_INTERVAL_SECONDS)

    except KeyboardInterrupt:
        print("\n Simulación detenida por el usuario.")
    finally:
        print(" Cerrando conexión con Kafka...")
        producer.close()
