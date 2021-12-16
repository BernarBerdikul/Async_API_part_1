from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends

from db.elastic import get_elastic
from db.redis import get_redis
from models.film import ESFilm, ListResponseFilm
from services.mixins import ServiceMixin
from services.pagination import get_by_pagination
from services.utils import get_hits, get_params_films_to_elastic, create_hash_key


class FilmService(ServiceMixin):
    async def get_all_films(
        self,
        page: int,
        page_size: int,
        sorting: str = None,
        query: str = None,
        genre: str = None,
    ) -> Optional[dict]:
        """Производим полнотекстовый поиск по фильмам в Elasticsearch."""
        _source: list[str] = ["id", "title", "imdb_rating", "genre"]

        params = f"{page}{page_size}{query}{genre}{sorting}"
        key = create_hash_key('movies', params)

        instance = await self._get_result_from_cache(key=key)
        if not instance:
            """Если данных нет в кеше, то ищем его в Elasticsearch"""
            body = get_params_films_to_elastic(
                page_size=page_size, page=page, genre=genre, query=query
            )
            docs: Optional[dict] = await self.search_in_elastic(
                body=body, _source=_source, sort=sorting
            )

            hits = get_hits(docs, ESFilm)

            films: list[ListResponseFilm] = [
                ListResponseFilm(
                    uuid=row.id, title=row.title, imdb_rating=row.imdb_rating
                )
                for row in hits
            ]

            """ Сохраняем фильм в кеш """
            data = orjson.dumps([i.dict() for i in films])
            await self._put_data_to_cache(key=key, instance=data)

            return get_by_pagination(
                name="films",
                db_objects=films,
                total=docs.get("hits").get("total").get("value", 0),
                page=page,
                page_size=page_size,
            )

        films_from_cache = [ListResponseFilm(**row) for row in orjson.loads(instance)]

        return get_by_pagination(
            name="films",
            db_objects=films_from_cache,
            total=len(films_from_cache),
            page=page,
            page_size=page_size,
        )


# get_film_service — это провайдер FilmService. Синглтон
@lru_cache()
def get_film_service(
    redis: Redis = Depends(get_redis),
    elastic: AsyncElasticsearch = Depends(get_elastic),
) -> FilmService:
    return FilmService(redis=redis, elastic=elastic, index="movies")
