import os
from dotenv import load_dotenv

load_dotenv('./.gitignore!/.env')

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = "DataBase/RobSpec.db"

