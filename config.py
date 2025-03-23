import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'ba4b22965324241b85e6aa45b670e9fa')    #python -c "import secrets; print(secrets.token_hex(16))"
    DB_HOST = os.getenv('DB_HOST', 'foodtell.cvui20wwwqc8.ap-southeast-1.rds.amazonaws.com')
    DB_PORT = os.getenv('DB_PORT', 5432)
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'foodtell_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'FoodTell123!')

    DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"