from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.core.config import CACHE_EXPIRE_IN_SECONDS
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.person import ElasticPerson, DetailResponsePerson
from src.services.pagination import get_by_pagination


class PersonService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "person"

    async def search_person(
        self, query: str, page: int, page_size: int
    ) -> Optional[dict]:
        try:
            body: dict = {
                "size": page_size,
                "from": (page - 1) * page_size,
                "query": {
                    "bool": {
                        "must": [
                            {"match": {"full_name": query}}
                        ]
                    }
                }
            }
            docs = await self.elastic.search(index=self.index, body=body)
            total: int = docs.get('hits').get('total').get("value", 0)
            hits: dict = docs.get('hits').get('hits')
            es_persons: List[ElasticPerson] = [
                ElasticPerson(**hit.get('_source'))
                for hit in hits
            ]
            persons: List[DetailResponsePerson] = [
                DetailResponsePerson(
                    uuid=es_person.id,
                    full_name=es_person.full_name,
                    role=es_person.roles[0],
                    film_ids=es_person.film_ids
                )
                for es_person in es_persons
            ]
            return get_by_pagination(
                name="persons",
                db_objects=persons,
                total=total,
                page=page,
                page_size=page_size
            )
        except NotFoundError:
            return None

    # get_by_id возвращает объект person
    async def get_by_id(self, person_id: str) -> Optional[ElasticPerson]:
        """ Пытаемся получить данные из кеша,
            потому что оно работает быстрее """
        person = await self._person_from_cache(person_id=person_id)
        if not person:
            """ Если персоны нет в кеше, то ищем его в Elasticsearch """
            person = await self._get_person_from_elastic(person_id=person_id)
            if not person:
                return None
            """ Сохраняем персону в кеш """
            await self._put_person_to_cache(person=person)
        return person

    async def _get_person_from_elastic(
        self, person_id: str
    ) -> Optional[ElasticPerson]:
        try:
            """ Если он отсутствует в Elasticsearch, значит,
                персоны вообще нет в базе """
            doc = await self.elastic.get(index=self.index, id=person_id)
            return ElasticPerson(**doc["_source"])
        except NotFoundError:
            return None

    async def _person_from_cache(
        self, person_id: str
    ) -> Optional[ElasticPerson]:
        """Пытаемся получить данные о персоне из кеша, используя команду get"""
        data = await self.redis.get(person_id)
        if not data:
            return None
        """создания объекта моделей из json"""
        person = ElasticPerson.parse_raw(data)
        return person

    async def _put_person_to_cache(self, person: ElasticPerson):
        """охраняем данные о персоне, время жизни кеша — 5 минут"""
        await self.redis.set(
            person.id, person.json(), expire=CACHE_EXPIRE_IN_SECONDS
        )


# get_person_service — это провайдер PersonService. Синглтон
@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis, elastic)
