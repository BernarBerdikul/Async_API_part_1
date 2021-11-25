from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import ElasticGenre

FILM_CACHE_EXPIRE_IN_SECONDS = 60 * 5  # 5 минут


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic

    # get_by_id возвращает объект жанра
    async def get_by_id(self, genre_id: str) -> Optional[ElasticGenre]:
        """ Пытаемся получить данные из кеша,
            потому что оно работает быстрее """
        genre = await self._genre_from_cache(genre_id=genre_id)
        if not genre:
            """ Если жанра нет в кеше, то ищем его в Elasticsearch """
            genre = await self._get_genre_from_elastic(genre_id=genre_id)
            if not genre:
                return None
            """ Сохраняем жанр в кеш """
            await self._put_genre_to_cache(genre=genre)
        return genre

    async def _get_genre_from_elastic(self, genre_id: str) -> Optional[ElasticGenre]:
        try:
            """ Если он отсутствует в Elasticsearch, значит,
                жанра вообще нет в базе """
            doc = await self.elastic.get("genre", genre_id)
            return ElasticGenre(**doc["_source"])
        except NotFoundError:
            return None

    async def _genre_from_cache(self, genre_id: str) -> Optional[ElasticGenre]:
        """Пытаемся получить данные о жанре из кеша, используя команду get"""
        data = await self.redis.get(genre_id)
        if not data:
            return None
        """создания объекта моделей из json"""
        genre = ElasticGenre.parse_raw(data)
        print(genre)
        return genre

    async def _put_genre_to_cache(self, genre: ElasticGenre):
        """охраняем данные о жанре, время жизни кеша — 5 минут"""
        await self.redis.set(
            genre.id, genre.json(), expire=FILM_CACHE_EXPIRE_IN_SECONDS
        )


# get_genre_service — это провайдер GenreService. Синглтон
@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
