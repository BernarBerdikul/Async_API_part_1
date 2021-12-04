from typing import Optional

from pydantic import parse_obj_as

from services.mixins import ES_schemas, Schemas


def get_params_films_to_elastic(
    page_size: int, page: int, genre: str = None, query: str = None
):
    """
    :param page:
    :param page_size:
    :param genre: фильтрует фильмы по жанру
    :param query: находит фильмы по полю title
    :return: возвращает правильный body для поиска в Elasticsearch
    """
    genre_search: list = []
    if genre:
        genre_search.append({"term": {"genre": genre}})
    if query:
        body: dict = {
            "size": page_size,
            "from": (page - 1) * page_size,
            "query": {
                "bool": {
                    "must": {"match": {"title": {"query": query, "fuzziness": "auto"}}},
                    "filter": genre_search,
                }
            },
        }
    else:
        body: dict = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {},
                    },
                    "filter": genre_search,
                }
            }
        }
    return body


def get_hits(docs: Optional[dict], schema: Schemas):
    hits: dict = docs.get("hits").get("hits")
    data = [row.get("_source") for row in hits]
    parse_data = parse_obj_as(list[schema], data)
    return parse_data
