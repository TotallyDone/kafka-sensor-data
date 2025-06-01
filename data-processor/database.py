import os
import psycopg2
from psycopg2 import sql
import time

def get_db_connection():
    max_retries = 10
    retry_delay = 5  # seconds

    for i in range(max_retries):
        try:
            conn = psycopg2.connect(
                host=os.getenv('POSTGRES_HOST', 'localhost'),
                database=os.getenv('POSTGRES_DB', 'sensor_data_db'),
                user=os.getenv('POSTGRES_USER', 'user'),
                password=os.getenv('POSTGRES_PASSWORD', 'password')
            )
            print("Successfully connected to PostgreSQL!")
            return conn
        except psycopg2.OperationalError as e:
            print(f"PostgreSQL connection failed (attempt {i+1}/{max_retries}): {e}")
            time.sleep(retry_delay)
    raise Exception("Could not connect to PostgreSQL after multiple retries.")


def create_tables(conn):
    with conn.cursor() as cur:
        # Table for all processed sensor readings
        cur.execute("""
            CREATE TABLE IF NOT EXISTS processed_sensor_readings (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                temperature FLOAT,
                humidity FLOAT,
                pressure FLOAT,
                status VARCHAR(50),
                processed_at TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        # Table for high temperature alerts
        cur.execute("""
            CREATE TABLE IF NOT EXISTS high_temp_alerts (
                id SERIAL PRIMARY KEY,
                sensor_id VARCHAR(50) NOT NULL,
                timestamp TIMESTAMPTZ NOT NULL,
                temperature FLOAT,
                humidity FLOAT,
                pressure FLOAT,
                alert_status VARCHAR(50), -- Stores the specific alert status like 'HIGH_TEMP_ALERT'
                alert_time TIMESTAMPTZ DEFAULT NOW()
            );
        """)
        conn.commit()
        print("Tables 'processed_sensor_readings' and 'high_temp_alerts' ensured to exist.")

# Function to insert into processed_sensor_readings table
def insert_processed_data(conn, data):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO processed_sensor_readings (sensor_id, timestamp, temperature, humidity, pressure, status)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (data['sensor_id'], data['timestamp'], data['temperature'], data['humidity'], data['pressure'], data['status'])
        )
        conn.commit()
        print(f"Inserted processed data for sensor {data['sensor_id']} at {data['timestamp']}")

#Function to insert into the high_temp_alerts table
def insert_alert_data(conn, data):
    with conn.cursor() as cur:
        cur.execute(
            """
            INSERT INTO high_temp_alerts (sensor_id, timestamp, temperature, humidity, pressure, alert_status)
            VALUES (%s, %s, %s, %s, %s, %s);
            """,
            (data['sensor_id'], data['timestamp'], data['temperature'], data['humidity'], data['pressure'], data['status']) # Note: using data['status'] for alert_status
        )
        conn.commit()
        print(f"Inserted HIGH TEMP ALERT for sensor {data['sensor_id']} at {data['timestamp']}")