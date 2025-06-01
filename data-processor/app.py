import os
import json
from kafka import KafkaConsumer, KafkaProducer
from database import get_db_connection, create_tables, insert_processed_data, insert_alert_data
from pydantic import BaseModel, Field, ValidationError

# Pydantic model 
class SensorReading(BaseModel):
    sensor_id: str = Field(..., example="sensor_001")
    timestamp: str = Field(..., example="2024-05-30T10:30:00Z")
    temperature: float = Field(..., ge=-50.0, le=100.0)
    humidity: float = Field(..., ge=0.0, le=100.0)
    pressure: float = Field(..., ge=900.0, le=1100.0)


def process_data(data): 
    processed_data = data
    
    if processed_data['temperature'] > 30: 
        processed_data['status'] = 'HIGH_TEMP_ALERT'
    else:
        processed_data['status'] = 'NORMAL'
    return processed_data

if __name__ == "__main__":
    kafka_broker = os.getenv('KAFKA_BROKER_URL', 'localhost:9092')
    kafka_input_topic = os.getenv('KAFKA_INPUT_TOPIC', 'raw_sensor_data')
    kafka_output_topic = os.getenv('KAFKA_OUTPUT_TOPIC', 'processed_sensor_data')
    kafka_dlq_topic = os.getenv('KAFKA_DLQ_TOPIC', 'raw_sensor_data_dlq') # Get DLQ topic

    consumer = KafkaConsumer(
        kafka_input_topic,
        bootstrap_servers=kafka_broker,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id='sensor-processor-group',
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )
    producer = KafkaProducer(
        bootstrap_servers=kafka_broker,
        value_serializer=lambda x: json.dumps(x).encode('utf-8')
    )

    db_conn = None
    try:
        db_conn = get_db_connection()
        create_tables(db_conn)

        print(f"Starting data processor. Consuming from topic: {kafka_input_topic} on broker: {kafka_broker}")

        for message in consumer:
            raw_data = message.value
            print(f"Received raw data: {raw_data}")

            try:
                # Validate incoming data using Pydantic
                validated_data = SensorReading(**raw_data).model_dump()
                processed_data = process_data(validated_data)

                if processed_data['status'] == 'HIGH_TEMP_ALERT':
                    insert_alert_data(db_conn, processed_data)
                else:
                    insert_processed_data(db_conn, processed_data)

                producer.send(kafka_output_topic, value=processed_data)
                print(f"Produced processed data to {kafka_output_topic}: {processed_data}")

            except ValidationError as e:
                print(f"Data validation error for message: {raw_data} - {e}. Sending to DLQ.")
                # DLQ LOGIC START
                try:
                    # Send the original raw_data to the DLQ topic
                    producer.send(kafka_dlq_topic, value=raw_data)
                    print(f"Sent invalid message to DLQ topic: {kafka_dlq_topic}")
                except Exception as producer_error:
                    print(f"Error sending to DLQ: {producer_error}")
                # DLQ LOGIC END
            except Exception as e:
                print(f"Error processing message: {e}. Message: {raw_data}")

    except Exception as e:
        print(f"Application failed to start: {e}")
    finally:
        if db_conn:
            db_conn.close()
        consumer.close()
        producer.close()
        print("Data processor stopped.")