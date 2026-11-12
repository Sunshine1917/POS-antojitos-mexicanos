import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
DB_NAME = os.getenv("DB_NAME", "antojitos_mexicanos.db")
DB_PATH = Path(__file__).resolve().parent / DB_NAME