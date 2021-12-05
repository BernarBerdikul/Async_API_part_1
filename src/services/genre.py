from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from services.utils import get_hits
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
        key = f'{page}{body}genre{page_size}'

        instance = await self._get_result_from_cache(key=key)
        if not instance:

            docs: Optional[dict] = await self.search_in_elastic(body=body)

            hits = get_hits(docs, ElasticGenre)

            genres: list[FilmGenre] = [
                FilmGenre(uuid=es_genre.id, name=es_genre.name)
                for es_genre in hits
            ]

            data = orjson.dumps([i.dict() for i in genres])
            await self._put_data_to_cache(key=key, instance=data)

            return get_by_pagination(
                name="genres",
                db_objects=genres,
                total=len(hits),
                page=page,
                page_size=page_size,
            )

        genres = [
            FilmGenre(**row) for row in orjson.loads(instance)
        ]

        return get_by_pagination(
            name="genres",
            db_objects=genres,
            total=len(genres),
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
