from functools import lru_cache
from typing import Optional

import orjson
from aioredis import Redis
from elasticsearch import AsyncElasticsearch
from fastapi import Depends
from pydantic import parse_obj_as

from src.db.elastic import get_elastic
from src.db.redis import get_redis
from src.models.film import ESFilm, ListResponseFilm
from src.services.mixins import ServiceMixin
from src.services.pagination import get_by_pagination
from src.services.utils import get_params_films_to_elastic


class FilmService(ServiceMixin):
    async def get_all_films(
        self,
        sorting: str,
        page: int,
        page_size: int,
        query: str = None,
        genre: str = None,
    ) -> Optional[dict]:
        """Производим полнотекстовый поиск по фильмам в Elasticsearch."""
        _source: list[str] = ["id", "title", "imdb_rating", "genre"]

        key = str(str(page) + str(page_size) + 'films' + str(query))

        instance = await self._result_from_cache_films(key=key, schema=ESFilm)
        if not instance:
            """Если данных нет в кеше, то ищем его в Elasticsearch"""
            body = get_params_films_to_elastic(
                page_size=page_size, page=page, genre=genre, query=query
            )
            docs: Optional[dict] = await self.search_in_elastic(
                body=body, _source=_source, sort=sorting
            )

            total: int = docs.get("hits").get("total").get("value", 0)
            hits: dict = docs.get("hits").get("hits")
            data = [row.get("_source") for row in hits]
            parse_data = parse_obj_as(list[ESFilm], data)
            films: list[ListResponseFilm] = [
                ListResponseFilm(
                    uuid=row.id, title=row.title, imdb_rating=row.imdb_rating
                )
                for row in parse_data
            ]

            """ Сохраняем фильм в кеш """
            await self._put_result_to_cache_films(key=key, instance=films)

            return get_by_pagination(
                name="films",
                db_objects=films,
                total=total,
                page=page,
                page_size=page_size,
            )

        films_from_cache = [
            ListResponseFilm(**row) for row in orjson.loads(instance)
        ]

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
