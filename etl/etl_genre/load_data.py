import logging
from contextlib import closing
from datetime import datetime
import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from config import dsl, es_conf
from elasticsearch_loader import ElasticSearchLoader
from postgres_loader import PostgresLoader
from services import backoff

logger = logging.getLogger('LoaderStart')


def load_from_postgres(pg_conn: _connection) -> list:
    postgres_loader = PostgresLoader(pg_conn)
    data = postgres_loader.loader_from_postgresql()
    return data


if __name__ == '__main__':
    columns = ['id', 'name']
    batch = 50

    @backoff()
    def query_postgres() -> list:
        with closing(psycopg2.connect(**dsl, cursor_factory=DictCursor)) as pg_conn:
            logger.info(f'{datetime.now()}\n\nустановлена связь с PostgreSQL. Начинаем загрузку данных')
            load_pq = load_from_postgres(pg_conn)
        return load_pq

    def save_elastic() -> None:
        """
        Загружаем пачками данные в ElasticSearch, предварительно создаем индекс в бд.
        """
        logger.info(f'{datetime.now()}\n\nустановлена связь с ElasticSearch. Начинаем загрузку данных')
        ElasticSearchLoader(es_conf).create_index('genre')
        data_from_postgres = query_postgres()
        count = len(data_from_postgres)
        index = 0
        movies = []
        while count != 0:
            if count >= batch:
                for row in data_from_postgres[index: index + batch]:
                    movies.append(dict(zip(columns, row)))
                    index += 1
                count -= batch
                ElasticSearchLoader(es_conf).load_data_to_elasticsearch(movies)
                movies.clear()
            else:
                ElasticSearchLoader(es_conf).load_data_to_elasticsearch(
                    [dict(zip(columns, row)) for row in data_from_postgres[index: index + count]]
                )
                count -= count
    save_elastic()
