import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(filename='etl.log', level='INFO')
logger = logging.getLogger()
logger.setLevel(level='INFO')


dsl = {
    'dbname': os.getenv('DB_NAME'),
    'user': os.getenv('POSTGRES_USER'),
    'password': os.getenv('POSTGRES_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'port': os.environ.get('DB_PORT'),
}

es_conf = [{
    'host': os.getenv('ES_HOST'),
    'port': os.getenv('ES_PORT'),
}]
