from functools import lru_cache
from typing import Optional, List, Tuple

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from pydantic import parse_obj_as

from src.core.config import CACHE_EXPIRE_IN_SECONDS
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import Film


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "movies"
        self._source = ['id', 'title', 'imdb_rating']

    # get_by_id возвращает объект фильма
    async def get_by_id(self, film_id: str) -> Optional[Film]:
        """ Пытаемся получить данные из кеша,
            потому что оно работает быстрее """
        film = await self._film_from_cache(film_id)
        if not film:
            """ Если фильма нет в кеше, то ищем его в Elasticsearch """
            film = await self._get_film_from_elastic(film_id)
            if not film:
                return None
            """ Сохраняем фильм в кеш """
            await self._put_film_to_cache(film)

        return film

    async def get_all_films(self, query: str = None) -> Optional[list[Film]]:
        """Производим полнотекстовый поиск по фильмам в Elasticsearch."""

        body = {
            "query": {
                "match": {
                    "title": {
                        "query": query,
                        "fuzziness": "auto"
                    }
                }
            }
        }

        if query is None:
            body = {
                "size": 2,
                "from": 0,
                "query": {
                    "match_all": {}
                }
            }

        try:
            docs = await self.elastic.search(
                index=self.index,
                _source=self._source,
                body=body,
                sort='imdb_rating:desc'
            )
            print(docs['hits']['total'])
            hits = docs.get('hits').get('hits')

            data = []
            for row in hits:
                data.append(row.get('_source'))
            return parse_obj_as(list[Film], data)

        except NotFoundError:
            return None

    async def _get_film_from_elastic(self, film_id: str) -> Optional[Film]:
        try:
            """ Если он отсутствует в Elasticsearch, значит,
                фильма вообще нет в базе """
            doc = await self.elastic.get(index=self.index, id=film_id)

            return Film(**doc["_source"])
        except NotFoundError:
            return None

    async def _film_from_cache(self, film_id: str) -> Optional[Film]:
        """Пытаемся получить данные о фильме из кеша, используя команду get"""
        data = await self.redis.get(film_id)
        if not data:
            return None
        """создания объекта моделей из json"""
        film = Film.parse_raw(data)

        return film

    async def _put_film_to_cache(self, film: Film):
        """охраняем данные о фильме, время жизни кеша — 5 минут"""
        await self.redis.set(
            film.id, film.json(), expire=CACHE_EXPIRE_IN_SECONDS
        )


# get_film_service — это провайдер FilmService. Синглтон
@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
