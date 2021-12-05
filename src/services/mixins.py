from typing import Optional, Union

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError

from src.core.config import CACHE_EXPIRE_IN_SECONDS
from src.models.film import ESFilm
from src.models.genre import ElasticGenre
from src.models.person import ElasticPerson

Schemas: tuple = (ESFilm, ElasticGenre, ElasticPerson)
ES_schemas = Union[Schemas]


class ServiceMixin:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch, index: str):
        self.redis = redis
        self.elastic = elastic
        self.index = index

    async def search_in_elastic(
        self, body: dict, _source=None, sort=None, _index=None
    ) -> Optional[dict]:
        if not _index:
            _index = self.index
        try:
            if sort[0] is not None:
                if sort[0][0] == "-":
                    sort = sort[0].removeprefix("-")
                    sort = sort + ":desc"
            else:
                sort = "imdb_rating:desc"
            return await self.elastic.search(
                index=_index, _source=_source, body=body, sort=sort
            )
        except NotFoundError:
            return None

    async def get_by_id(self, target_id: str, schema: Schemas) -> Optional[ES_schemas]:
        """Пытаемся получить данные из кеша, потому что оно работает быстрее"""
        instance = await self._get_result_from_cache(key=target_id)
        if not instance:
            """Если данных нет в кеше, то ищем его в Elasticsearch"""
            instance = await self._get_data_from_elastic_by_id(
                target_id=target_id, schema=schema
            )
            if not instance:
                return None
            """ Сохраняем фильм в кеш """
            await self._put_data_to_cache(key=instance.id, instance=instance.json())
            return instance
        return schema.parse_raw(instance)

    async def _get_data_from_elastic_by_id(
        self, target_id: str, schema: Schemas
    ) -> Optional[ES_schemas]:
        """Если он отсутствует в Elastic, значит объекта вообще нет в базе"""
        try:
            doc = await self.elastic.get(index=self.index, id=target_id)
            return schema(**doc["_source"])
        except NotFoundError:
            return None

    async def _get_result_from_cache(self, key: str) -> bytes or None:
        """Пытаемся получить данные об объекте из кеша"""
        data = await self.redis.get(key=key)
        if not data:
            return None
        """создания объекта моделей из json"""
        return data

    async def _put_data_to_cache(self, key: str, instance: bytes or str) -> None:
        """Сохраняем данные об объекте в кеш, время жизни кеша — 5 минут"""
        await self.redis.set(
            key=key,
            value=instance,
            expire=CACHE_EXPIRE_IN_SECONDS,
        )

