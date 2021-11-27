import os
from logging import config as logging_config
from pathlib import Path

from src.core.logger import LOGGING

from dotenv import load_dotenv

<<<<<<< HEAD
load_dotenv()
=======
env_path = Path(__file__).resolve().parent.parent.parent / "envs/fastapi.env"
load_dotenv(dotenv_path=env_path)
>>>>>>> etl_gesammelt

# Применяем настройки логирования
logging_config.dictConfig(LOGGING)

# Версия сервиса
VERSION = "0.1.0"

# Название проекта. Используется в Swagger-документации
PROJECT_NAME = os.getenv('PROJECT_NAME', 'movies')

# Настройки Redis
REDIS_HOST = os.getenv('REDIS_HOST', '127.0.0.1')
REDIS_PORT = int(os.getenv('REDIS_PORT', 6379))

# Настройки Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST', '127.0.0.1')
ELASTIC_PORT = int(os.getenv('ELASTIC_PORT', 9200))

# Корень проекта
<<<<<<< HEAD
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
=======
BASE_DIR = Path(__file__).resolve().parent.parent
>>>>>>> etl_gesammelt
