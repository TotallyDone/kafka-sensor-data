# Real-Time IoT Data Pipeline

This project demonstrates a complete real-time data pipeline for simulated IoT sensor readings, from data generation and Apache Kafka messaging to processing and PostgreSQL persistence.

## 🚀 Project Overview

This solution is designed to showcase core data engineering principles. It simulates IoT sensor data, streams it through Apache Kafka, processes it with a Python application, and finally stores the processed data in a PostgreSQL database for persistent storage.

### Key Components:

1.  **Sensor Data Generator (`sensor-generator`):** A Python application that simulates IoT devices generating real-time temperature, humidity, and pressure readings. These readings are then sent to Apache Kafka.
2.  **Apache Kafka:** A distributed streaming platform used as a robust and scalable message broker to handle the high-throughput, real-time data streams.
3.  **Data Processor (`data-processor`):** A Python application that continuously consumes raw data from Kafka. It validates the incoming data using Pydantic, applies simple business logic (e.g., adds a 'status' based on temperature), and then stores the refined data into a PostgreSQL database. It also has the capability to re-publish processed data to a different Kafka topic.
4.  **PostgreSQL:** A powerful open-source relational database used for reliable and persistent storage of the processed sensor readings.

## 💡 Technologies Used

* **Python:** For developing the data generation and processing applications.
    * `kafka-python`: Python client library for interacting with Kafka.
    * `psycopg2`: PostgreSQL adapter for Python.
    * `Pydantic`: For defining data schemas and performing data validation, ensuring data quality.
* **Docker & Docker Compose:** Essential for containerizing each service (Python apps, Kafka, PostgreSQL) and orchestrating them, allowing for easy setup, deployment, and isolation.
* **Apache Kafka:** The backbone for real-time data streaming.
* **PostgreSQL:** The robust database for data persistence.


## 🚀 How to Run the Data Pipeline

### Prerequisites

* **Docker Desktop:** Ensure Docker and Docker Compose are installed and running on your system.
    * [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)

### Steps

1.  **Clone the Repository:**
    Open your terminal or command prompt and clone this repository:
    ```bash
    git clone [https://github.com/TotallyDone/kafka-sensor-data.git](https://github.com/TotallyDone/kafka-sensor-data.git)
    cd kafka-sensor-data
    ```

2.  **Start the Services:**
    Build and run all the Docker containers defined in `docker-compose.yml` in detached mode (`-d`). This command will set up the entire streaming pipeline.
    ```bash
    docker compose up --build -d
    ```
    This command will perform the following actions:
    * Build Docker images for your `sensor-generator` and `data-processor` applications based on their respective `Dockerfile`s.
    * Download official Docker images for Kafka (along with its dependency Zookeeper) and PostgreSQL.
    * Create and start all these services, establishing a virtual network for them to communicate.

3.  **Verify Data Flow (Optional but Recommended):**
    You can observe the logs of the running containers to ensure data is flowing as expected:

    * **Sensor Generator Logs:** See sensor data being produced and sent to Kafka.
        ```bash
        docker compose logs sensor-generator -f
        ```
    * **Data Processor Logs:** See raw data being received from Kafka, processed, and messages indicating storage in PostgreSQL.
        ```bash
        docker compose logs data-processor -f
        ```
    * **PostgreSQL Data:** Connect to the PostgreSQL database directly to confirm that data is being inserted.
        ```bash
        docker exec -it postgres-db psql -U user -d sensor_data_db
        ```
        Once connected to the `psql` command line, run the following SQL query to see the latest entries:
        ```sql
        SELECT * FROM processed_sensor_readings ORDER BY timestamp DESC LIMIT 10;
        ```
        (Don't forget the semicolon `;` at the end of the SQL query!)
        To exit the `psql` terminal, type `\q` and press Enter.

4.  **Stop the Services:**
    When you are finished running the pipeline, you can stop and remove all containers, associated networks, and volumes:
    ```bash
    docker compose down -v
    ```
    The `-v` flag is important here as it removes the named volume where PostgreSQL stores its data. This ensures a clean slate if you want to restart the pipeline from scratch later.



