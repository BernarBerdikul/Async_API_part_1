from functools import lru_cache
from http import HTTPStatus
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends, HTTPException

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import ESFilm, ListResponseFilm
from src.models.person import DetailResponsePerson, ElasticPerson
from src.services.mixins import ServiceMixin
from src.services.pagination import get_by_pagination


class PersonService(ServiceMixin):
    async def get_person(self, person_id: str):
        person = await self.get_by_id(target_id=person_id, schema=ElasticPerson)
        if not person:
            """Если персона не найдена, отдаём 404 статус"""
            raise HTTPException(
                status_code=HTTPStatus.NOT_FOUND, detail="person not found"
            )
        return person

    async def get_person_films(
        self, film_ids: list[str], page: int, page_size: int
    ) -> Optional[dict]:
        body: dict = {
            "size": page_size,
            "from": (page - 1) * page_size,
            "query": {"ids": {"values": film_ids}},
        }
        docs: Optional[dict] = await self.search_in_elastic(body=body, _index="movies")
        if docs:
            total: int = docs.get("hits").get("total").get("value", 0)
            hits: dict = docs.get("hits").get("hits")
            es_films: list[ESFilm] = [ESFilm(**hit.get("_source")) for hit in hits]
            person_films: list[ListResponseFilm] = [
                ListResponseFilm(
                    uuid=film.id, title=film.title, imdb_rating=film.imdb_rating
                )
                for film in es_films
            ]
            return get_by_pagination(
                name="films",
                db_objects=person_films,
                total=total,
                page=page,
                page_size=page_size,
            )

    async def search_person(
        self, query: str, page: int, page_size: int
    ) -> Optional[dict]:
        body: dict = {
            "size": page_size,
            "from": (page - 1) * page_size,
            "query": {"bool": {"must": [{"match": {"full_name": query}}]}},
        }
        docs: Optional[dict] = await self.search_in_elastic(body=body)
        if docs:
            total: int = docs.get("hits").get("total").get("value", 0)
            hits: dict = docs.get("hits").get("hits")
            es_persons: list[ElasticPerson] = [
                ElasticPerson(**hit.get("_source")) for hit in hits
            ]
            persons: list[DetailResponsePerson] = [
                DetailResponsePerson(
                    uuid=es_person.id,
                    full_name=es_person.full_name,
                    role=es_person.roles[0],
                    film_ids=es_person.film_ids,
                )
                for es_person in es_persons
            ]
            return get_by_pagination(
                name="persons",
                db_objects=persons,
                total=total,
                page=page,
                page_size=page_size,
            )


# get_person_service — это провайдер PersonService. Синглтон
@lru_cache()
def get_person_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> PersonService:
    return PersonService(redis=redis, elastic=elastic, index="person")
