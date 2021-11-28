import enum
from typing import Optional
from fastapi import Query


class FilmSortImdbRating(str, enum.Enum):
    descending = 'imdb_rating:desc'
    ascending = 'imdb_rating'


def get_params_films_to_elastic(genre: str = None, query: str = None):
    """
    :param genre: фильтрует фильмы по жанру
    :param query: находит фильмы по полю title
    :return: возвращает правильный body для поиска в Elasticsearch
    """
    if genre is None:
        genre_search = []
    else:
        genre_search = [{"term": {"genre": genre}}]

    body = {
        "query": {
            "bool": {
                "must": {
                    "match": {
                        "title": {
                            "query": query,
                            "fuzziness": "auto"
                        }
                    }
                },
                "filter": genre_search
            }
        }}

    if query is None:
        body = {
            "query": {
                "bool": {
                    "must": {
                        "match_all": {},
                    },
                    "filter": genre_search
                }
            }}

    return body


class FilmQueryParams:
    """
    Класс задает параметры для поиска по фильму
    """
    def __init__(
        self,
        sort_imdb_rating: FilmSortImdbRating = Query(
            FilmSortImdbRating.descending,
            title='Сортировка по рейтингу',
            description='Сортирует по возрастанию и убыванию',
        ),
        genre_filter: Optional[str] = Query(
            None,
            title='Фильтр жанров',
            description='Фильтрует фильмы по жанрам',
            alias='filter[genre]'
        ),
        query: str = Query(
            None,
            title='Запрос',
            description='Осуществляет поиск по названию фильма',
        ),


    ) -> None:
        self.sort = sort_imdb_rating,
        self.genre_filter = genre_filter
        self.query = query
