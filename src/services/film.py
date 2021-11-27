from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import ElasticFilm

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class FilmService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект фильма
    async def get_by_id(self, film_id: str) -> Optional[ElasticFilm]:
        """ Пытаемся получить данные из кеша,
            потому что оно работает быстрее """
        film = await self._film_from_cache(film_id=film_id)
        if not film:
            """ Если фильма нет в кеше, то ищем его в Elasticsearch """
            film = await self._get_film_from_elastic(film_id=film_id)
            if not film:
                return None
            """ Сохраняем фильм в кеш """
            await self._put_film_to_cache(film=film)

        return film

    async def _get_film_from_elastic(self, film_id: str) -> Optional[ElasticFilm]:
        try:
            """ Если он отсутствует в Elasticsearch, значит,
                фильма вообще нет в базе """
            doc = await self.elastic.get("movies", film_id)
            return ElasticFilm(**doc["_source"])
        except NotFoundError:
            return None

    async def _film_from_cache(self, film_id: str) -> Optional[ElasticFilm]:
        """Пытаемся получить данные о фильме из кеша, используя команду get"""
        data = await self.redis.get(film_id)
        if not data:
            return None
        """создания объекта моделей из json"""
        film = ElasticFilm.parse_raw(data)
        return film

    async def _put_film_to_cache(self, film: ElasticFilm):
        """охраняем данные о фильме, время жизни кеша — 5 минут"""
        await self.redis.set(
            film.id, film.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


# get_film_service — это провайдер FilmService. Синглтон
@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis, elastic)
