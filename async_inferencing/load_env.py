from dotenv import load_dotenv
from pathlib import Path 

def load_env():
    env_path = Path('.') / 'secrets.env'
    if(load_dotenv(dotenv_path=env_path)):
        print("Environment variables loaded from secrets.env")
    else:
        print("****Environment variables NOT loaded from environment****")

load_env()