Install docker using this URI:

```
https://docs.docker.com/engine/install/ubuntu/
```

Configure docker to work without root:
```
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```

Check if docker can be run without root:
```
docker run hello-world
```

Reboot if still got error:
```
reboot
```

For more detail about docker config refer to this URI:
```
https://stackoverflow.com/questions/48957195/how-to-fix-docker-got-permission-denied-issue
```

Make sure .env file exists in the main folder containing environments mentioned below:

```
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9093'
KAFKA_TOPIC_PIZZA = 'pizza_events'
KAFKA_TOPIC_CHECKOUT = 'checkout_events'
KAFKA_CONSUMER_GROUP = '1'

POSTGRES_PASSWORD=postgrespass
POSTGRES_PORT=5433
POSTGRES_USER=postgres
POSTGRES_HOST=localhost
POSTGRES_DB=postgres

MONGO_USERNAME=user
MONGO_PASSWORD=pass
MONGO_HOST=localhost
MONGO_PORT=27017
```

You can use your own creds.

Create .streamlit folder containing secrets.toml file which should have mongo creds:

```
[mongo]
host = "localhost"
port = 27017
username = "user"
password = "pass"
```

Run change_mongo_pass.sh to adjust passwords mongo

To start the system just run start.sh on linux

Before starting make sure all the packages are installed using:

```
pip install -r requirements.txt
```
