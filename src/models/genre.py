from typing import List
from pydantic import BaseModel
from src.models.mixin import BaseModelMixin, PaginationMixin


class ElasticGenre(BaseModel):
    id: str
    name: str


class FilmGenre(BaseModelMixin):
    """ Schema for Film work detail """
    name: str


class DetailResponseGenre(FilmGenre):
    """ Schema for Genre detail """
    # film_ids: Optional[List[UUID]] = []


class GenrePagination(PaginationMixin):
    genres: List[FilmGenre] = []
