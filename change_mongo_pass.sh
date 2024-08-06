#!/bin/bash

# Define the path to the Mongo directory
MONGO_DIR="./Mongo/data"
ENV_FILE="./Mongo/.env"
SECRETS_FILE="./StreamlitApp/.streamlit/secrets.toml"
EVENTS_CONSUMER_ENV_FILE="./.env"

if [ "$(docker ps -aq -f name=mongo)" ]; then
    echo "Mongo container exists. Removing it..."
    docker compose down -v
fi

# Check if the data folder exists
if [ -d "$MONGO_DIR" ]; then
  echo "Data folder exists. Deleting..."
  sudo rm -rf "$MONGO_DIR"
  echo "Data folder deleted."
else
  echo "Data folder does not exist."
fi

# Prompt the user to change the MongoDB username and password
read -p "Enter new MongoDB username: " new_username
read -sp "Enter new MongoDB password: " new_password
echo

# Update the .env file with the new credentials
if [ -f "$ENV_FILE" ]; then
  sed -i "s/^MONGO_INITDB_ROOT_USERNAME=.*/MONGO_INITDB_ROOT_USERNAME=$new_username/" "$ENV_FILE"
  sed -i "s/^MONGO_INITDB_ROOT_PASSWORD=.*/MONGO_INITDB_ROOT_PASSWORD=$new_password/" "$ENV_FILE"
  echo "Updated MongoDB credentials in Mongo/.env file."
else
  echo "MONGO_INITDB_ROOT_USERNAME=$new_username" >> "$ENV_FILE"
  echo "MONGO_INITDB_ROOT_PASSWORD=$new_password" >> "$ENV_FILE"
  echo "Mongo/.env file created with new MongoDB credentials."
fi

if [ -f "$SECRETS_FILE" ]; then
    sed -i "s/^username = .*/username = \"$new_username\"/" "$SECRETS_FILE"
    sed -i "s/^password = .*/password = \"$new_password\"/" "$SECRETS_FILE"
    echo "Updated MongoDB credentials in secrets.toml file."
else
    echo "[mongo]" >> "$SECRETS_FILE"
    echo "host = \"localhost\"" >> "$SECRETS_FILE"
    echo "port = 27017" >> "$SECRETS_FILE"
    echo "username = \"$new_username\"" >> "$SECRETS_FILE"
    echo "password = \"$new_password\"" >> "$SECRETS_FILE"
    echo "secrets.toml file created with new MongoDB credentials."
fi

# Update the EventsConsumer/.env file with the new credentials
if [ -f "$EVENTS_CONSUMER_ENV_FILE" ]; then
  sed -i "s/^MONGO_USERNAME=.*/MONGO_USERNAME=$new_username/" "$EVENTS_CONSUMER_ENV_FILE"
  sed -i "s/^MONGO_PASSWORD=.*/MONGO_PASSWORD=$new_password/" "$EVENTS_CONSUMER_ENV_FILE"
  echo "Updated MongoDB credentials in .env file."
else
  echo "MONGO_USERNAME=$new_username" > "$EVENTS_CONSUMER_ENV_FILE"
  echo "MONGO_PASSWORD=$new_password" >> "$EVENTS_CONSUMER_ENV_FILE"
  echo "MONGO_HOST=localhost" >> "$EVENTS_CONSUMER_ENV_FILE"
  echo "MONGO_PORT=27017" >> "$EVENTS_CONSUMER_ENV_FILE"
  echo ".env file created with new MongoDB credentials."
fi