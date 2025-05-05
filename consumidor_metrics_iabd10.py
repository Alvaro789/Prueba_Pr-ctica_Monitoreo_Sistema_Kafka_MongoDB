from kafka import KafkaConsumer
from pymongo import MongoClient
from datetime import datetime, timezone
import json
import time

# --- Configuración ---
TOPIC = "system-metrics-topic-iabd10"
GROUP_ID = "grupo_iabd10_id"
KAFKA_BROKER = "172.18.48.1:29092"  
MONGO_URI = "mongodb+srv://iabd10:iabdiabd10@cluster0.tu9ht.mongodb.net/"
DB_NAME = "monitoring_db"
RAW_COLLECTION = "system_metrics_raw_iabd10"
KPIS_COLLECTION = "system_metrics_kpis_iabd10"
WINDOW_SIZE = 20

# --- Conexiones ---
try:
    print("Conectando a MongoDB Atlas...")
    mongo_client = MongoClient(MONGO_URI)
    db = mongo_client[DB_NAME]
    raw_col = db[RAW_COLLECTION]
    kpi_col = db[KPIS_COLLECTION]
    print("Conexión a MongoDB Atlas exitosa.")
except Exception as e:
    print(f"Error al conectar a MongoDB: {e}")
    exit(1)

try:
    print("Conectando a Kafka...")
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=[KAFKA_BROKER],
        group_id=GROUP_ID,
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    print(f"Suscrito al topic: {TOPIC}")
except Exception as e:
    print(f"Error al conectar a Kafka: {e}")
    exit(1)

# --- Variables para KPIs ---
buffer = []
start_time = time.time()

# --- Consumo de mensajes ---
try:
    for message in consumer:
        metric = message.value
        print(f"Recibiendo mensaje: {metric}")  # Imprimir mensaje recibido
        raw_col.insert_one(metric)  # Guardar mensaje crudo en MongoDB
        print(f"Mensaje insertado en {RAW_COLLECTION} en MongoDB.")  # Confirmación de inserción

        buffer.append(metric)

        if len(buffer) >= WINDOW_SIZE:
            print(f"\nCalculando KPIs para ventana de {WINDOW_SIZE} mensajes...")

            cpu_avg = sum(m["metrics"]["cpu_percent"] for m in buffer) / WINDOW_SIZE
            mem_avg = sum(m["metrics"]["memory_percent"] for m in buffer) / WINDOW_SIZE
            disk_avg = sum(m["metrics"]["disk_io_mbps"] for m in buffer) / WINDOW_SIZE
            net_avg = sum(m["metrics"]["network_mbps"] for m in buffer) / WINDOW_SIZE
            error_sum = sum(m["metrics"]["error_count"] for m in buffer)

            end_time = time.time()
            duration = end_time - start_time
            rate = WINDOW_SIZE / duration if duration > 0 else 0

            kpi_doc = {
                "timestamp_kpi_utc": datetime.now(timezone.utc).isoformat(),
                "window_duration_secs": round(duration, 2),
                "num_messages": WINDOW_SIZE,
                "kpis": {
                    "cpu_avg_percent": round(cpu_avg, 2),
                    "memory_avg_percent": round(mem_avg, 2),
                    "disk_avg_mbps": round(disk_avg, 2),
                    "network_avg_mbps": round(net_avg, 2),
                    "total_errors": error_sum,
                    "processing_rate_msgs_per_sec": round(rate, 2)
                }
            }

            kpi_col.insert_one(kpi_doc)
            print(f"KPIs calculados: {kpi_doc}")  # Imprimir KPIs calculados
            print(f"KPIs insertados en {KPIS_COLLECTION} en MongoDB.")  # Confirmación de inserción

            buffer = []
            start_time = time.time()

except KeyboardInterrupt:
    print("\nInterrumpido por el usuario.")
except Exception as e:
    print(f"Error durante el procesamiento: {e}")
finally:
    print("Cerrando conexiones...")
    consumer.close()
    mongo_client.close()
