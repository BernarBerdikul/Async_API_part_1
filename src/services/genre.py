from functools import lru_cache
from typing import Optional

from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.genre import ElasticGenre, FilmGenre
from src.services.mixins import ServiceMixin
from src.services.pagination import get_by_pagination


class GenreService(ServiceMixin):

    # get_genres_list возвращает список объектов жанра
    async def get_genres_list(self, page: int, page_size: int) -> Optional[dict]:
        body: dict = {
            "size": page_size,
            "from": (page - 1) * page_size,
            "query": {"match_all": {}},
        }
        docs: Optional[dict] = await self.search_in_elastic(body=body)
        if docs:
            total: int = docs.get("hits").get("total").get("value", 0)
            hits: dict = docs.get("hits").get("hits")
            es_genres: list[ElasticGenre] = [
                ElasticGenre(**hit.get("_source")) for hit in hits
            ]
            genres: list[FilmGenre] = [
                FilmGenre(uuid=es_genre.id, name=es_genre.name)
                for es_genre in es_genres
            ]
            return get_by_pagination(
                name="genres",
                db_objects=genres,
                total=total,
                page=page,
                page_size=page_size,
            )


# get_genre_service — это провайдер GenreService. Синглтон
@lru_cache()
def get_genre_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> GenreService:
    return GenreService(redis=redis, elastic=elastic, index="genre")
