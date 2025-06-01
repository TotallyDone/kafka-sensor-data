import os
import time
import json
import random
from datetime import datetime, timezone
from kafka import KafkaProducer
from pydantic import BaseModel, Field
import uuid

# Pydantic model
class SensorReading(BaseModel):
    sensor_id: str = Field(..., example="sensor_001")
    timestamp: str = Field(..., example="2024-05-30T10:30:00Z")
    temperature: float = Field(..., ge=-50.0, le=100.0)
    humidity: float = Field(..., ge=0.0, le=100.0)
    pressure: float = Field(..., ge=900.0, le=1100.0)

def generate_sensor_data(sensor_id_prefix="sensor"):
    sensor_id = f"{sensor_id_prefix}_{uuid.uuid4().hex[:3]}"

    current_dt = datetime.now(timezone.utc)
    timestamp_str = current_dt.isoformat(timespec='seconds')
    if timestamp_str.endswith('+00:00'):
        timestamp_str = timestamp_str[:-6]
    timestamp_str += 'Z'

    data_to_send = {
        "sensor_id": sensor_id,
        "timestamp": timestamp_str,
        "temperature": round(random.uniform(15.0, 35.0), 2), #  "temperature": "bad data",  <---switch to this for bad data 
        "humidity": round(random.uniform(40.0, 70.0), 2),
        "pressure": round(random.uniform(980.0, 1020.0), 2)
    }
    # Directly dump the dictionary to JSON and encode it
    return json.dumps(data_to_send).encode('utf-8')
    

if __name__ == "__main__":
    kafka_broker = os.getenv('KAFKA_BROKER_URL', 'localhost:9092')
    kafka_topic = os.getenv('KAFKA_TOPIC', 'raw_sensor_data')
    generation_interval = int(os.getenv('GENERATION_INTERVAL_SECONDS', 2))

    producer = KafkaProducer(bootstrap_servers=kafka_broker)
    print(f"Starting sensor data generator. Producing to topic: {kafka_topic} on broker: {kafka_broker}")

    try:
        while True:
            data = generate_sensor_data()
            producer.send(kafka_topic, value=data)
            print(f"Produced: {data.decode('utf-8')}")
            time.sleep(generation_interval)
    except KeyboardInterrupt:
        print("Stopping producer.")
        producer.close()