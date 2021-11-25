import json
import logging
from datetime import datetime
from elasticsearch import Elasticsearch
from esindex import CINEMA_INDEX_BODY
from services import backoff
from state import JsonFileStorage, State

logger = logging.getLogger('ESLoader')


class ElasticSearchLoader:
    def __init__(self, host: list, state_key='key'):
        self.client = Elasticsearch(host)
        self.data = []
        self.key = state_key

    @backoff()
    def create_index(self, index: str) -> None:
        """
        Создаем индекс для Elasticsearch.
        """
        if not self.client.indices.exists(index):
            self.client.indices.create(index=index, ignore=400, body=CINEMA_INDEX_BODY)
            logger.warning(f'{datetime.now()}\n\nиндекс {index} создан')
        logger.warning(f'{datetime.now()}\n\nиндекс {index} был создан ранее')

    @backoff()
    def bulk_data_to_elasticsearch(self) -> None:
        self.client.bulk(index='person', body=self.data, refresh=True)

    def load_data_to_elasticsearch(self, query) -> None:
        """
        Загружаем данные пачками в Elasticsearch предварительно присваивая записям id.
        """
        data_json = json.dumps(query)
        load_json = json.loads(data_json)

        for row in load_json:
            self.data.append({"create": {"_index": "person", "_id": row['id']}})
            self.data.append(row)
            self.bulk_data_to_elasticsearch()
            self.data.clear()
        State(JsonFileStorage('postgres_data.txt')).set_state(str(self.key), value=str(datetime.now()))

