from dotenv import load_dotenv
import os

def main():
    
    load_dotenv()
    print("TOPIC:", os.getenv("KAFKA_TOPIC_PIZZA"))
    print("TOPIC:", os.getenv("KAFKA_TOPIC_CHECKOUT"))
    
if __name__ == "__main__":
    main()