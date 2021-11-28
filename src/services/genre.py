from functools import lru_cache
from typing import Optional, List

from aioredis import Redis
from elasticsearch import AsyncElasticsearch, NotFoundError
from fastapi import Depends

from src.core.config import CACHE_EXPIRE_IN_SECONDS
from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import ElasticGenre, FilmGenre
from src.services.pagination import get_by_pagination


class GenreService:
    def __init__(self, redis: Redis, elastic: AsyncElasticsearch):
        self.redis = redis
        self.elastic = elastic
        self.index = "genre"

    # get_genres_list возвращает список объектов жанра
    async def get_genres_list(
        self, page: int, page_size: int
    ) -> Optional[dict]:
        try:
            body: dict = {
                "size": page_size,
                "from": (page - 1) * page_size,
                "query": {
                    "match_all": {}
                }
            }
            docs = await self.elastic.search(index=self.index, body=body)
            total: int = docs.get('hits').get('total').get("value", 0)
            hits: dict = docs.get('hits').get('hits')
            es_genres: List[ElasticGenre] = [
                ElasticGenre(**hit.get('_source'))
                for hit in hits
            ]
            genres: List[FilmGenre] = [
                FilmGenre(uuid=es_genre.id, name=es_genre.name)
                for es_genre in es_genres
            ]
            return get_by_pagination(
                name="genres",
                db_objects=genres,
                total=total,
                page=page,
                page_size=page_size
            )
        except NotFoundError:
            return None

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
            doc = await self.elastic.get(index=self.index, id=genre_id)
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
        return genre

    async def _put_genre_to_cache(self, genre: ElasticGenre):
        """охраняем данные о жанре, время жизни кеша — 5 минут"""
        await self.redis.set(
            genre.id, genre.json(), expire=CACHE_EXPIRE_IN_SECONDS
        )


# get_genre_service — это провайдер GenreService. Синглтон
@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis, elastic)
