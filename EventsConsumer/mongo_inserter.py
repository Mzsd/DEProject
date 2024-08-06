import pymongo


def save_to_mongo(data, db_name, coll_name, mongo_uri="mongodb://localhost:27017/"):
    """
    Save data to a MongoDB collection.

    :param data: The data to be inserted (should be a dictionary or a list of dictionaries).
    :param db_name: The name of the database.
    :param mongo_uri: The MongoDB URI (default is "mongodb://localhost:27017/").
    """
    try:
        # Create a MongoDB client
        client = pymongo.MongoClient(mongo_uri)
        
        # Access the specified database
        db = client[db_name]
        
        # Access the specified collection
        collection = db[coll_name]
        
        # Insert the data into the collection
        if isinstance(data, list):
            collection.insert_many(data)
        else:
            collection.insert_one(data)
        
        print("Data inserted successfully")
    
    except pymongo.errors.PyMongoError as e:
        print(f"An error occurred: {e}")
    
    finally:
        # Close the MongoDB client
        client.close()