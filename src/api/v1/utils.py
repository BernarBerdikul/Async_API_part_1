import enum
from typing import Optional

from fastapi import Query


class FilmSortImdbRating(str, enum.Enum):
    descending = "imdb_rating:desc"
    ascending = "imdb_rating"


class FilmQueryParams:
    """
    Класс задает параметры для поиска по фильму
    """

    def __init__(
        self,
        sort_imdb_rating: FilmSortImdbRating = Query(
            FilmSortImdbRating.descending,
            title="Сортировка по рейтингу",
            description="Сортирует по возрастанию и убыванию",
        ),
        genre_filter: Optional[str] = Query(
            None,
            title="Фильтр жанров",
            description="Фильтрует фильмы по жанрам",
            alias="filter[genre]",
        ),
        query: str = Query(
            None,
            title="Запрос",
            description="Осуществляет поиск по названию фильма",
        ),
    ) -> None:
        self.sort = (sort_imdb_rating,)
        self.genre_filter = genre_filter
        self.query = query
