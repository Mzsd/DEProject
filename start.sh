#!/bin/bash

# Check if Kafka container exists
if [ "$(docker ps -aq -f name=kafka)" ]; then
    echo "Kafka container exists. Removing it..."
    docker compose down -v
fi

# Start docker-compose
docker compose up -d

cd postgres

# Execute table_gen.py inside postgres directory
python table_gen.py

cd ..

# Open a new terminal and run the Python script
gnome-terminal -- bash -c "python3 "./EventsConsumer/consumer.py"; exec bash"

# Open a new terminal and run Streamlit App
gnome-terminal -- bash -c "cd ./StreamlitApp && streamlit run "app.py"; exec bash"

uvicorn main:app --reload

